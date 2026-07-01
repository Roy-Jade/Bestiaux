import random
import uuid

from bestiaux.breeding.domain import are_related, generate_wild_genome
from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import AlleleEntity
from bestiaux.models.genetics import TraitCategory


def _allele(id_: str, *, is_dominant: bool = False) -> AlleleEntity:
    return AlleleEntity(
        id=id_,
        trait_category=TraitCategory.EYES,
        name=id_,
        is_dominant=is_dominant,
        sprite_key="",
    )


def _baseline_allele_lookup() -> dict[str, AlleleEntity]:
    return {allele_id: _allele(allele_id) for allele_id in BASELINE_ALLELES.values()}


def _baseline_pool() -> dict[str, list[str]]:
    return {cat.value: [BASELINE_ALLELES[cat]] for cat in TraitCategory}


class TestAreRelated:
    def test_unrelated_creatures_are_not_related(self) -> None:
        # GIVEN
        p1 = uuid.uuid4()
        p2 = uuid.uuid4()
        ancestors1: set[uuid.UUID] = {uuid.uuid4(), uuid.uuid4()}
        ancestors2: set[uuid.UUID] = {uuid.uuid4(), uuid.uuid4()}

        # WHEN / THEN
        assert not are_related(ancestors1, ancestors2, p1, p2)

    def test_parent_is_ancestor_of_other(self) -> None:
        # GIVEN — parent1 appears in parent2's ancestry
        p1 = uuid.uuid4()
        p2 = uuid.uuid4()
        ancestors1: set[uuid.UUID] = set()
        ancestors2: set[uuid.UUID] = {p1}

        # WHEN / THEN
        assert are_related(ancestors1, ancestors2, p1, p2)

    def test_shared_ancestor_detected(self) -> None:
        # GIVEN
        p1, p2 = uuid.uuid4(), uuid.uuid4()
        shared = uuid.uuid4()
        ancestors1 = {shared, uuid.uuid4()}
        ancestors2 = {shared, uuid.uuid4()}

        # WHEN / THEN
        assert are_related(ancestors1, ancestors2, p1, p2)

    def test_parent2_in_parent1_ancestry(self) -> None:
        # GIVEN — p2 is an ancestor of p1 (parent of parent1)
        p1, p2 = uuid.uuid4(), uuid.uuid4()
        ancestors1 = {p2}
        ancestors2: set[uuid.UUID] = set()

        # WHEN / THEN
        assert are_related(ancestors1, ancestors2, p1, p2)


class TestGenerateWildGenome:
    def test_produces_all_trait_categories(self) -> None:
        # GIVEN
        pool = _baseline_pool()
        alleles = _baseline_allele_lookup()

        # WHEN
        genome = generate_wild_genome(pool, alleles, random.Random(1))

        # THEN
        assert set(genome.genes.keys()) == set(TraitCategory)

    def test_baseline_only_pool_produces_baseline_genome(self) -> None:
        # GIVEN
        pool = _baseline_pool()
        alleles = _baseline_allele_lookup()

        # WHEN
        genome = generate_wild_genome(pool, alleles, random.Random(1))

        # THEN
        for trait_category, gene in genome.genes.items():
            expected = BASELINE_ALLELES[trait_category]
            assert gene.allele_from_parent1 == expected
            assert gene.allele_from_parent2 == expected

    def test_pool_with_extra_allele_can_produce_non_baseline(self) -> None:
        # GIVEN — EYES pool has baseline + dominant
        pool = _baseline_pool()
        pool[TraitCategory.EYES.value] = ["round_eyes", "almond_eyes"]
        alleles = _baseline_allele_lookup()
        alleles["almond_eyes"] = AlleleEntity(
            id="almond_eyes",
            trait_category=TraitCategory.EYES,
            name="Almond eyes",
            is_dominant=True,
            sprite_key="",
        )

        # WHEN — run many times
        rng = random.Random(99)
        expressed_set = {
            generate_wild_genome(pool, alleles, rng).genes[TraitCategory.EYES].expressed_allele
            for _ in range(100)
        }

        # THEN — at least one run produced the dominant allele
        assert "almond_eyes" in expressed_set
