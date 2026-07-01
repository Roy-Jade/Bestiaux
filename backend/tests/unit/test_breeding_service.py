import uuid
from datetime import UTC, datetime

import pytest

from bestiaux.breeding.service import BreedingService
from bestiaux.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from bestiaux.creature.domain import CreatureEntity
from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import AlleleEntity, Genome, create_baseline_genome
from bestiaux.models.creature import LifeStage
from bestiaux.models.genetics import TraitCategory


class FakeCreatureRepository:
    def __init__(self, creatures: list[CreatureEntity] | None = None) -> None:
        self.creatures: list[CreatureEntity] = creatures or []

    async def get_by_id(self, creature_id: uuid.UUID) -> CreatureEntity | None:
        return next((c for c in self.creatures if c.id == creature_id), None)

    async def get_active_for_user(self, user_id: uuid.UUID) -> CreatureEntity | None:
        return next((c for c in self.creatures if c.owner_id == user_id and c.is_active), None)

    async def create(self, creature: CreatureEntity) -> CreatureEntity:
        self.creatures.append(creature)
        return creature

    async def save(self, creature: CreatureEntity) -> None:
        for i, c in enumerate(self.creatures):
            if c.id == creature.id:
                self.creatures[i] = creature
                return


class FakeAncestorRepository:
    def __init__(self, ancestors: dict[uuid.UUID, set[uuid.UUID]] | None = None) -> None:
        self.ancestors = ancestors or {}

    async def get_all_ancestors(self, creature_id: uuid.UUID) -> set[uuid.UUID]:
        return self.ancestors.get(creature_id, set())


class FakeAlleleRepository:
    async def get_all(self) -> dict[str, AlleleEntity]:
        return {
            allele_id: AlleleEntity(
                id=allele_id,
                trait_category=cat,
                name=allele_id,
                is_dominant=False,
                sprite_key="",
            )
            for cat, allele_id in BASELINE_ALLELES.items()
        }


class FakeGenomeRepository:
    def __init__(self) -> None:
        self.genomes: dict[uuid.UUID, Genome] = {}

    async def get_by_creature_id(self, creature_id: uuid.UUID) -> Genome | None:
        return self.genomes.get(creature_id)

    async def save(self, creature_id: uuid.UUID, genome: Genome) -> None:
        self.genomes[creature_id] = genome


class FakeWildPoolRepository:
    def __init__(self) -> None:
        self.pool: dict[str, list[str]] = {cat.value: [] for cat in TraitCategory}
        self.unlocked: list[str] = []

    async def get_unlocked_for_user(self, user_id: uuid.UUID) -> dict[str, list[str]]:
        return self.pool

    async def unlock(self, user_id: uuid.UUID, allele_id: str) -> None:
        self.unlocked.append(allele_id)


def _make_service(
    creatures: list[CreatureEntity] | None = None,
    ancestors: dict[uuid.UUID, set[uuid.UUID]] | None = None,
    genomes: dict[uuid.UUID, Genome] | None = None,
) -> tuple[BreedingService, FakeCreatureRepository, FakeGenomeRepository]:
    creature_repo = FakeCreatureRepository(creatures or [])
    genome_repo = FakeGenomeRepository()
    if genomes:
        genome_repo.genomes = genomes
    service = BreedingService(
        creature_repo=creature_repo,
        ancestor_repo=FakeAncestorRepository(ancestors or {}),
        allele_repo=FakeAlleleRepository(),
        genome_repo=genome_repo,
        pool_repo=FakeWildPoolRepository(),
    )
    return service, creature_repo, genome_repo


def _adult(user_id: uuid.UUID, generation: int = 1) -> CreatureEntity:
    now = datetime.now(UTC)
    return CreatureEntity(
        owner_id=user_id,
        name="Parent",
        life_stage=LifeStage.ADULT,
        generation=generation,
        is_active=False,
        is_alive=True,
        stage_started_at=now,
        last_interaction_at=now,
    )


class TestBreedWithWild:
    async def test_creates_child_with_genome(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        parent = _adult(user_id)
        genome_repo_data = {parent.id: create_baseline_genome()}
        service, _creature_repo, genome_repo = _make_service(
            creatures=[parent], genomes=genome_repo_data
        )

        # WHEN
        child = await service.breed_with_wild(user_id, parent.id)

        # THEN
        assert child.generation == 2
        assert child.parent1_id == parent.id
        assert child.is_active
        assert child.id in genome_repo.genomes

    async def test_parent_reproduction_count_incremented(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        parent = _adult(user_id)
        service, creature_repo, _ = _make_service(
            creatures=[parent], genomes={parent.id: create_baseline_genome()}
        )

        # WHEN
        await service.breed_with_wild(user_id, parent.id)

        # THEN
        saved = await creature_repo.get_by_id(parent.id)
        assert saved is not None
        assert saved.reproduction_count == 1

    async def test_young_adult_transitions_to_adult(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        parent = CreatureEntity(
            owner_id=user_id,
            name="Parent",
            life_stage=LifeStage.YOUNG_ADULT,
            generation=1,
            is_active=True,
            is_alive=True,
            stage_started_at=now,
            last_interaction_at=now,
        )
        service, creature_repo, _ = _make_service(
            creatures=[parent], genomes={parent.id: create_baseline_genome()}
        )

        # WHEN
        child = await service.breed_with_wild(user_id, parent.id)

        # THEN
        saved_parent = await creature_repo.get_by_id(parent.id)
        assert saved_parent is not None
        assert saved_parent.life_stage == LifeStage.ADULT
        assert not saved_parent.is_active
        assert child.is_active

    async def test_rejects_ineligible_parent(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        parent = CreatureEntity(
            owner_id=user_id,
            name="Baby",
            life_stage=LifeStage.BABY,
            generation=1,
            is_active=True,
            is_alive=True,
            stage_started_at=now,
            last_interaction_at=now,
        )
        service, _, _ = _make_service(creatures=[parent])

        # WHEN / THEN
        with pytest.raises(ConflictError, match="not eligible"):
            await service.breed_with_wild(user_id, parent.id)

    async def test_rejects_wrong_owner(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        other_user = uuid.uuid4()
        parent = _adult(other_user)
        service, _, _ = _make_service(
            creatures=[parent], genomes={parent.id: create_baseline_genome()}
        )

        # WHEN / THEN
        with pytest.raises(ForbiddenError):
            await service.breed_with_wild(user_id, parent.id)


class TestBreedOwned:
    async def test_creates_child_from_two_parents(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        p1 = _adult(user_id, generation=1)
        p2 = _adult(user_id, generation=2)
        service, _, genome_repo = _make_service(
            creatures=[p1, p2],
            genomes={p1.id: create_baseline_genome(), p2.id: create_baseline_genome()},
        )

        # WHEN
        child = await service.breed_owned(user_id, p1.id, p2.id)

        # THEN
        assert child.generation == 3
        assert child.parent1_id == p1.id
        assert child.parent2_id == p2.id
        assert child.id in genome_repo.genomes

    async def test_rejects_related_parents(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        p1 = _adult(user_id)
        p2 = _adult(user_id)
        shared_ancestor = uuid.uuid4()
        service, _, _ = _make_service(
            creatures=[p1, p2],
            ancestors={p1.id: {shared_ancestor}, p2.id: {shared_ancestor}},
        )

        # WHEN / THEN
        with pytest.raises(ForbiddenError, match="same lineage"):
            await service.breed_owned(user_id, p1.id, p2.id)

    async def test_rejects_missing_genome(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        p1 = _adult(user_id)
        p2 = _adult(user_id)
        service, _, _ = _make_service(creatures=[p1, p2])  # no genomes

        # WHEN / THEN
        with pytest.raises(NotFoundError, match="genome"):
            await service.breed_owned(user_id, p1.id, p2.id)
