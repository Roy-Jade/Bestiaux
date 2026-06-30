import uuid

from bestiaux.core.exceptions import NotFoundError
from bestiaux.genetics.domain import Genome, create_baseline_genome, inherit_genome
from bestiaux.genetics.protocols import IAlleleRepository, ICreatureGenomeRepository


class GeneticsService:
    def __init__(
        self,
        allele_repo: IAlleleRepository,
        genome_repo: ICreatureGenomeRepository,
    ) -> None:
        self.allele_repo = allele_repo
        self.genome_repo = genome_repo

    async def assign_baseline_genome(self, creature_id: uuid.UUID) -> Genome:
        genome = create_baseline_genome()
        await self.genome_repo.save(creature_id, genome)
        return genome

    async def breed_genome(
        self,
        parent1_id: uuid.UUID,
        parent2_id: uuid.UUID,
        parent1_biome_id: str | None,
        parent2_biome_id: str | None,
    ) -> Genome:
        parent1_genome = await self.genome_repo.get_by_creature_id(parent1_id)
        parent2_genome = await self.genome_repo.get_by_creature_id(parent2_id)
        if parent1_genome is None or parent2_genome is None:
            raise NotFoundError("Both parents must have an assigned genome")

        alleles = await self.allele_repo.get_all()
        return inherit_genome(
            parent1_genome,
            parent2_genome,
            parent1_biome_id,
            parent2_biome_id,
            alleles,
        )
