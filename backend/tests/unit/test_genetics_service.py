import uuid

import pytest

from bestiaux.core.exceptions import NotFoundError
from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import AlleleEntity, Genome, create_baseline_genome
from bestiaux.genetics.service import GeneticsService
from bestiaux.models.genetics import TraitCategory


class FakeAlleleRepository:
    def __init__(self, alleles: dict[str, AlleleEntity] | None = None) -> None:
        self.alleles = alleles or {
            allele_id: AlleleEntity(
                id=allele_id,
                trait_category=trait_category,
                name=allele_id,
                is_dominant=False,
                sprite_key="",
            )
            for trait_category, allele_id in BASELINE_ALLELES.items()
        }

    async def get_all(self) -> dict[str, AlleleEntity]:
        return self.alleles


class FakeCreatureGenomeRepository:
    def __init__(self) -> None:
        self.genomes: dict[uuid.UUID, Genome] = {}

    async def get_by_creature_id(self, creature_id: uuid.UUID) -> Genome | None:
        return self.genomes.get(creature_id)

    async def save(self, creature_id: uuid.UUID, genome: Genome) -> None:
        self.genomes[creature_id] = genome


class TestAssignBaselineGenome:
    async def test_assigns_and_persists_baseline_genome(self) -> None:
        # GIVEN
        allele_repo = FakeAlleleRepository()
        genome_repo = FakeCreatureGenomeRepository()
        service = GeneticsService(allele_repo=allele_repo, genome_repo=genome_repo)
        creature_id = uuid.uuid4()

        # WHEN
        genome = await service.assign_baseline_genome(creature_id)

        # THEN
        assert genome_repo.genomes[creature_id] is genome
        assert set(genome.genes.keys()) == set(TraitCategory)


class TestBreedGenome:
    async def test_breeds_two_baseline_parents(self) -> None:
        # GIVEN
        allele_repo = FakeAlleleRepository()
        genome_repo = FakeCreatureGenomeRepository()
        service = GeneticsService(allele_repo=allele_repo, genome_repo=genome_repo)
        parent1_id, parent2_id = uuid.uuid4(), uuid.uuid4()
        genome_repo.genomes[parent1_id] = create_baseline_genome()
        genome_repo.genomes[parent2_id] = create_baseline_genome()

        # WHEN
        child_genome = await service.breed_genome(parent1_id, parent2_id, None, None)

        # THEN
        assert set(child_genome.genes.keys()) == set(TraitCategory)

    async def test_raises_if_parent_has_no_genome(self) -> None:
        # GIVEN
        allele_repo = FakeAlleleRepository()
        genome_repo = FakeCreatureGenomeRepository()
        service = GeneticsService(allele_repo=allele_repo, genome_repo=genome_repo)
        parent1_id, parent2_id = uuid.uuid4(), uuid.uuid4()
        genome_repo.genomes[parent1_id] = create_baseline_genome()
        # parent2 has no genome assigned

        # WHEN / THEN
        with pytest.raises(NotFoundError, match="Both parents must have an assigned genome"):
            await service.breed_genome(parent1_id, parent2_id, None, None)
