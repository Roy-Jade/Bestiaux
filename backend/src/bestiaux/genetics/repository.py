import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.genetics.domain import AlleleEntity, CreatureGene, Genome
from bestiaux.models.genetics import Allele, CreatureGenome, TraitCategory, WildGenePool


class AlleleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self) -> dict[str, AlleleEntity]:
        result = await self.session.execute(select(Allele))
        return {
            allele.id: AlleleEntity(
                id=allele.id,
                trait_category=allele.trait_category,
                name=allele.name,
                is_dominant=allele.is_dominant,
                sprite_key=allele.sprite_key,
                biome_id=allele.biome_id,
            )
            for allele in result.scalars()
        }


class CreatureGenomeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_creature_id(self, creature_id: uuid.UUID) -> Genome | None:
        result = await self.session.execute(
            select(CreatureGenome).where(CreatureGenome.creature_id == creature_id)
        )
        rows = result.scalars().all()
        if not rows:
            return None

        genes = {
            row.trait_category: CreatureGene(
                trait_category=row.trait_category,
                allele_from_parent1=row.allele_from_parent1,
                allele_from_parent2=row.allele_from_parent2,
                expressed_allele=row.expressed_allele,
            )
            for row in rows
        }
        return Genome(genes=genes)

    async def save(self, creature_id: uuid.UUID, genome: Genome) -> None:
        for gene in genome.genes.values():
            self.session.add(
                CreatureGenome(
                    creature_id=creature_id,
                    trait_category=gene.trait_category,
                    allele_from_parent1=gene.allele_from_parent1,
                    allele_from_parent2=gene.allele_from_parent2,
                    expressed_allele=gene.expressed_allele,
                )
            )
        await self.session.commit()


class WildPoolRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_unlocked_for_user(self, user_id: uuid.UUID) -> dict[str, list[str]]:
        result = await self.session.execute(
            select(WildGenePool, Allele)
            .join(Allele, WildGenePool.allele_id == Allele.id)
            .where(WildGenePool.user_id == user_id)
        )
        pool: dict[str, list[str]] = {cat.value: [] for cat in TraitCategory}
        for row in result:
            pool[row.Allele.trait_category.value].append(row.WildGenePool.allele_id)
        return pool

    async def unlock(self, user_id: uuid.UUID, allele_id: str) -> None:
        existing = await self.session.execute(
            select(WildGenePool).where(
                WildGenePool.user_id == user_id, WildGenePool.allele_id == allele_id
            )
        )
        if existing.scalar_one_or_none() is not None:
            return
        self.session.add(WildGenePool(user_id=user_id, allele_id=allele_id))
        await self.session.commit()
