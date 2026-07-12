import uuid
from typing import ClassVar

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

    _BIRTH_TRAITS: ClassVar[set[TraitCategory]] = {TraitCategory.COLOR, TraitCategory.EYES}

    async def unlock_for_birth(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Unlocks COLOR and EYES expressed alleles if non-baseline (called at birth)."""
        genome = await self.genome_repo.get_by_creature_id(creature_id)
        if genome is None:
            return

        for category in self._BIRTH_TRAITS:
            gene = genome.genes.get(category)
            if gene is None:
                continue
            if gene.expressed_allele != BASELINE_ALLELES[category]:
                await self.pool_repo.unlock(user_id, gene.expressed_allele)

    async def unlock_for_child_stage(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Unlocks non-birth-trait expressed alleles when creature reaches CHILD stage."""
        genome = await self.genome_repo.get_by_creature_id(creature_id)
        if genome is None:
            return

        for category, gene in genome.genes.items():
            if category in self._BIRTH_TRAITS:
                continue
            if gene.expressed_allele != BASELINE_ALLELES[category]:
                await self.pool_repo.unlock(user_id, gene.expressed_allele)
