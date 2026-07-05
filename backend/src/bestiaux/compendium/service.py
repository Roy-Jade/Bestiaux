import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.compendium.domain import all_possible_form_ids, compute_form_id
from bestiaux.models.biome import Biome
from bestiaux.models.creature import Creature
from bestiaux.models.genetics import Allele, CreatureGenome, WildGenePool


@dataclass
class FormEntry:
    form_id: str
    biome_id: str
    level: int
    dominant_stats: list[str]
    discovered: bool
    latest_creature_id: uuid.UUID | None
    latest_creature_name: str | None


@dataclass
class CreatureSummary:
    id: uuid.UUID
    name: str
    generation: int
    life_stage: str
    is_alive: bool
    is_active: bool
    biome_id: str | None
    form_id: str | None
    training_force: float
    training_beauty: float
    training_size: float
    max_stage_reached: str
    created_at: object


@dataclass
class AlleleDetail:
    id: str
    trait_category: str
    name: str
    is_dominant: bool
    sprite_key: str


@dataclass
class GenomeGene:
    trait_category: str
    allele_from_parent1: str
    allele_from_parent2: str
    expressed_allele: str


@dataclass
class CreatureDetail:
    id: uuid.UUID
    name: str
    generation: int
    life_stage: str
    is_alive: bool
    biome_id: str | None
    form_id: str | None
    training_force: float
    training_beauty: float
    training_size: float
    autonomy: float
    hunger: float
    health: float
    happiness: float
    genome: list[GenomeGene]
    parent1_id: uuid.UUID | None
    parent2_id: uuid.UUID | None
    created_at: object


class CompendiumService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_forms(self, user_id: uuid.UUID) -> list[FormEntry]:
        biome_ids = await self._get_all_biome_ids()
        all_forms = all_possible_form_ids(biome_ids)

        creatures = await self._get_user_creatures_with_biome(user_id)
        # Map form_id → most recent creature with that form (by created_at)
        best_by_form: dict[str, Creature] = {}
        for creature in creatures:
            if creature.biome_id is None:
                continue
            fid = compute_form_id(
                creature.biome_id,
                creature.training_force,
                creature.training_beauty,
                creature.training_size,
            )
            existing = best_by_form.get(fid)
            if existing is None or (
                creature.created_at
                and existing.created_at
                and creature.created_at > existing.created_at
            ):
                best_by_form[fid] = creature

        entries = []
        for form_id in all_forms:
            parts = form_id.split("_", 1)
            biome_id = parts[0]
            code = parts[1] if len(parts) > 1 else "0"

            if code == "0":
                level = 0
                dominant = []
            else:
                level = int(code[0])
                dominant = list(code[1:])

            best = best_by_form.get(form_id)
            entries.append(
                FormEntry(
                    form_id=form_id,
                    biome_id=biome_id,
                    level=level,
                    dominant_stats=dominant,
                    discovered=best is not None,
                    latest_creature_id=best.id if best else None,
                    latest_creature_name=best.name if best else None,
                )
            )
        return entries

    async def get_history(self, user_id: uuid.UUID) -> list[CreatureSummary]:
        result = await self.session.execute(
            select(Creature)
            .where(Creature.owner_id == user_id)
            .order_by(Creature.generation, Creature.created_at)
        )
        creatures = result.scalars().all()
        summaries = []
        for c in creatures:
            form_id = (
                compute_form_id(c.biome_id, c.training_force, c.training_beauty, c.training_size)
                if c.biome_id
                else None
            )
            summaries.append(
                CreatureSummary(
                    id=c.id,
                    name=c.name,
                    generation=c.generation,
                    life_stage=c.life_stage,
                    is_alive=c.is_alive,
                    is_active=c.is_active,
                    biome_id=c.biome_id,
                    form_id=form_id,
                    training_force=c.training_force,
                    training_beauty=c.training_beauty,
                    training_size=c.training_size,
                    max_stage_reached=c.max_stage_reached,
                    created_at=c.created_at,
                )
            )
        return summaries

    async def get_creature_detail(
        self, user_id: uuid.UUID, creature_id: uuid.UUID
    ) -> CreatureDetail | None:
        result = await self.session.execute(
            select(Creature).where(Creature.id == creature_id, Creature.owner_id == user_id)
        )
        creature = result.scalar_one_or_none()
        if creature is None:
            return None

        genome_result = await self.session.execute(
            select(CreatureGenome).where(CreatureGenome.creature_id == creature_id)
        )
        genes = [
            GenomeGene(
                trait_category=g.trait_category,
                allele_from_parent1=g.allele_from_parent1,
                allele_from_parent2=g.allele_from_parent2,
                expressed_allele=g.expressed_allele,
            )
            for g in genome_result.scalars().all()
        ]

        form_id = (
            compute_form_id(
                creature.biome_id,
                creature.training_force,
                creature.training_beauty,
                creature.training_size,
            )
            if creature.biome_id
            else None
        )

        return CreatureDetail(
            id=creature.id,
            name=creature.name,
            generation=creature.generation,
            life_stage=creature.life_stage,
            is_alive=creature.is_alive,
            biome_id=creature.biome_id,
            form_id=form_id,
            training_force=creature.training_force,
            training_beauty=creature.training_beauty,
            training_size=creature.training_size,
            autonomy=creature.autonomy,
            hunger=creature.hunger,
            health=creature.health,
            happiness=creature.happiness,
            genome=genes,
            parent1_id=creature.parent1_id,
            parent2_id=creature.parent2_id,
            created_at=creature.created_at,
        )

    async def get_unlocked_alleles(self, user_id: uuid.UUID) -> list[AlleleDetail]:
        result = await self.session.execute(
            select(Allele)
            .join(WildGenePool, WildGenePool.allele_id == Allele.id)
            .where(WildGenePool.user_id == user_id)
            .order_by(Allele.trait_category, Allele.id)
        )
        return [
            AlleleDetail(
                id=a.id,
                trait_category=a.trait_category,
                name=a.name,
                is_dominant=a.is_dominant,
                sprite_key=a.sprite_key,
            )
            for a in result.scalars().all()
        ]

    async def _get_all_biome_ids(self) -> list[str]:
        result = await self.session.execute(select(Biome.id))
        return list(result.scalars().all())

    async def _get_user_creatures_with_biome(self, user_id: uuid.UUID) -> list[Creature]:
        result = await self.session.execute(
            select(Creature).where(Creature.owner_id == user_id, Creature.biome_id.isnot(None))
        )
        return list(result.scalars().all())
