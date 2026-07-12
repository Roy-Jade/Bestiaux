import uuid
from datetime import UTC, datetime

from bestiaux.breeding.domain import are_related, generate_wild_genome
from bestiaux.breeding.protocols import IAncestorRepository
from bestiaux.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from bestiaux.creature.domain import CreatureEntity
from bestiaux.creature.protocols import ICreatureRepository
from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import inherit_genome
from bestiaux.genetics.protocols import (
    IAlleleRepository,
    ICreatureGenomeRepository,
    IWildPoolRepository,
)
from bestiaux.genetics.wild_pool_service import WildPoolService
from bestiaux.models.creature import LifeStage


class BreedingService:
    def __init__(
        self,
        creature_repo: ICreatureRepository,
        ancestor_repo: IAncestorRepository,
        allele_repo: IAlleleRepository,
        genome_repo: ICreatureGenomeRepository,
        pool_repo: IWildPoolRepository,
    ) -> None:
        self.creature_repo = creature_repo
        self.ancestor_repo = ancestor_repo
        self.allele_repo = allele_repo
        self.genome_repo = genome_repo
        self.pool_repo = pool_repo
        self._wild_pool_svc = WildPoolService(genome_repo=genome_repo, pool_repo=pool_repo)

    async def breed_with_wild(self, user_id: uuid.UUID, parent_id: uuid.UUID) -> CreatureEntity:
        parent = await self._get_eligible_parent(parent_id, user_id)

        parent_genome = await self.genome_repo.get_by_creature_id(parent_id)
        if parent_genome is None:
            raise NotFoundError("Parent has no genome")

        alleles = await self.allele_repo.get_all()
        pool_with_baseline = await self._build_pool_for_user(user_id)
        wild_genome = generate_wild_genome(pool_with_baseline, alleles)
        child_genome = inherit_genome(parent_genome, wild_genome, parent.biome_id, None, alleles)

        parent_generation = parent.generation
        await self._finalize_parent(parent)
        await self._finalize_active_ya_if_any(user_id, exclude={parent_id})

        child = await self._create_child(
            user_id=user_id,
            parent1_id=parent_id,
            parent2_id=None,
            generation=parent_generation + 1,
        )
        await self.genome_repo.save(child.id, child_genome)
        await self._wild_pool_svc.unlock_for_birth(child.id, user_id)
        return child

    async def breed_owned(
        self,
        user_id: uuid.UUID,
        parent1_id: uuid.UUID,
        parent2_id: uuid.UUID,
    ) -> CreatureEntity:
        parent1 = await self._get_eligible_parent(parent1_id, user_id)
        parent2 = await self._get_eligible_parent(parent2_id, user_id)

        ancestors1 = await self.ancestor_repo.get_all_ancestors(parent1_id)
        ancestors2 = await self.ancestor_repo.get_all_ancestors(parent2_id)
        if are_related(ancestors1, ancestors2, parent1_id, parent2_id):
            raise ForbiddenError("Cannot breed creatures from the same lineage")

        parent1_genome = await self.genome_repo.get_by_creature_id(parent1_id)
        parent2_genome = await self.genome_repo.get_by_creature_id(parent2_id)
        if parent1_genome is None or parent2_genome is None:
            raise NotFoundError("Both parents must have an assigned genome")

        alleles = await self.allele_repo.get_all()
        child_genome = inherit_genome(
            parent1_genome, parent2_genome, parent1.biome_id, parent2.biome_id, alleles
        )

        max_generation = max(parent1.generation, parent2.generation)
        await self._finalize_parent(parent1)
        await self._finalize_parent(parent2)
        await self._finalize_active_ya_if_any(user_id, exclude={parent1_id, parent2_id})

        child = await self._create_child(
            user_id=user_id,
            parent1_id=parent1_id,
            parent2_id=parent2_id,
            generation=max_generation + 1,
        )
        await self.genome_repo.save(child.id, child_genome)
        await self._wild_pool_svc.unlock_for_birth(child.id, user_id)
        return child

    async def _get_eligible_parent(
        self, creature_id: uuid.UUID, user_id: uuid.UUID
    ) -> CreatureEntity:
        creature = await self.creature_repo.get_by_id(creature_id)
        if creature is None:
            raise NotFoundError("Creature not found")
        if creature.owner_id != user_id:
            raise ForbiddenError("Creature does not belong to this user")
        if not creature.can_reproduce():
            raise ConflictError("Creature is not eligible for reproduction")
        return creature

    async def _create_child(
        self,
        user_id: uuid.UUID,
        parent1_id: uuid.UUID,
        parent2_id: uuid.UUID | None,
        generation: int,
    ) -> CreatureEntity:
        now = datetime.now(UTC)
        child = CreatureEntity(
            owner_id=user_id,
            name="",
            generation=generation,
            parent1_id=parent1_id,
            parent2_id=parent2_id,
            stage_started_at=now,
            last_interaction_at=now,
            is_active=True,
        )
        return await self.creature_repo.create(child)

    async def _finalize_parent(self, parent: CreatureEntity) -> None:
        parent.reproduction_count += 1
        if parent.life_stage == LifeStage.YOUNG_ADULT:
            parent.life_stage = LifeStage.ADULT
            parent.is_active = False
        await self.creature_repo.save(parent)

    async def _finalize_active_ya_if_any(self, user_id: uuid.UUID, exclude: set[uuid.UUID]) -> None:
        """Transitions the current active YA to adult if it is not one of the breeding parents."""
        active = await self.creature_repo.get_active_for_user(user_id)
        if active is None or active.id in exclude:
            return
        if active.life_stage == LifeStage.YOUNG_ADULT:
            active.life_stage = LifeStage.ADULT
            active.is_active = False
            await self.creature_repo.save(active)

    async def get_compatible_partners(
        self, user_id: uuid.UUID, parent_id: uuid.UUID
    ) -> list[CreatureEntity]:
        """Returns creatures that can breed with parent_id (no consanguinity, under quota)."""
        candidates = await self.creature_repo.get_eligible_parents_for_user(user_id)
        parent_ancestors = await self.ancestor_repo.get_all_ancestors(parent_id)

        compatible = []
        for candidate in candidates:
            if candidate.id == parent_id:
                continue
            candidate_ancestors = await self.ancestor_repo.get_all_ancestors(candidate.id)
            if not are_related(parent_ancestors, candidate_ancestors, parent_id, candidate.id):
                compatible.append(candidate)
        return compatible

    async def _build_pool_for_user(self, user_id: uuid.UUID) -> dict[str, list[str]]:
        user_pool = await self.pool_repo.get_unlocked_for_user(user_id)
        return {
            cat.value: [BASELINE_ALLELES[cat], *user_pool.get(cat.value, [])]
            for cat in BASELINE_ALLELES
        }
