import uuid

from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.protocols import ICreatureGenomeRepository, IWildPoolRepository
from bestiaux.models.genetics import TraitCategory


class WildPoolService:
    def __init__(
        self,
        genome_repo: ICreatureGenomeRepository,
        pool_repo: IWildPoolRepository,
    ) -> None:
        self.genome_repo = genome_repo
        self.pool_repo = pool_repo

    async def unlock_for_birth(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Unlocks COLOR expressed allele if non-baseline (called at birth)."""
        genome = await self.genome_repo.get_by_creature_id(creature_id)
        if genome is None:
            return

        color_gene = genome.genes.get(TraitCategory.COLOR)
        if color_gene is None:
            return

        baseline = BASELINE_ALLELES[TraitCategory.COLOR]
        if color_gene.expressed_allele != baseline:
            await self.pool_repo.unlock(user_id, color_gene.expressed_allele)

    async def unlock_for_child_stage(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Unlocks non-COLOR expressed alleles when creature reaches CHILD stage."""
        genome = await self.genome_repo.get_by_creature_id(creature_id)
        if genome is None:
            return

        for category, gene in genome.genes.items():
            if category == TraitCategory.COLOR:
                continue
            if gene.expressed_allele != BASELINE_ALLELES[category]:
                await self.pool_repo.unlock(user_id, gene.expressed_allele)
