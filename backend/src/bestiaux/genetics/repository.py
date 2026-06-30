import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.genetics.domain import AlleleEntity, CreatureGene, Genome
from bestiaux.models.genetics import Allele, CreatureGenome


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
