import random

from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import (
    AlleleEntity,
    CreatureGene,
    Genome,
    apply_mutation,
    create_baseline_genome,
    inherit_genome,
    resolve_expression,
    select_allele,
    transmit_allele,
)
from bestiaux.models.genetics import TraitCategory


def _allele(id_: str, *, is_dominant: bool) -> AlleleEntity:
    return AlleleEntity(
        id=id_, trait_category=TraitCategory.EYES, name=id_, is_dominant=is_dominant, sprite_key=""
    )


class TestCreateBaselineGenome:
    def test_all_traits_present(self) -> None:
        # WHEN
        genome = create_baseline_genome()

        # THEN
        assert set(genome.genes.keys()) == set(TraitCategory)

    def test_uses_baseline_alleles_for_both_parents(self) -> None:
        # WHEN
        genome = create_baseline_genome()

        # THEN
        for trait_category, expected_allele in BASELINE_ALLELES.items():
            gene = genome.genes[trait_category]
            assert gene.allele_from_parent1 == expected_allele
            assert gene.allele_from_parent2 == expected_allele
            assert gene.expressed_allele == expected_allele


class TestSelectAllele:
    def test_returns_one_of_the_two_alleles_as_selected(self) -> None:
        # GIVEN
        rng = random.Random(1)

        # WHEN
        selected, other = select_allele(("a", "b"), rng)

        # THEN
        assert {selected, other} == {"a", "b"}
        assert selected != other

    def test_is_roughly_50_50_over_many_runs(self) -> None:
        # GIVEN
        rng = random.Random(42)
        results = [select_allele(("a", "b"), rng)[0] for _ in range(1000)]

        # WHEN
        count_a = results.count("a")

        # THEN
        assert 400 < count_a < 600


class TestApplyMutation:
    def test_v1_returns_selected_allele_unchanged(self) -> None:
        # WHEN
        result = apply_mutation("selected_allele", "other_allele", biome_id="marine")

        # THEN
        assert result == "selected_allele"

    def test_ignores_biome(self) -> None:
        # WHEN
        result = apply_mutation("selected_allele", "other_allele", biome_id=None)

        # THEN
        assert result == "selected_allele"


class TestTransmitAllele:
    def test_transmits_one_of_the_parent_pair(self) -> None:
        # GIVEN
        rng = random.Random(7)

        # WHEN
        result = transmit_allele(("a", "b"), biome_id=None, rng=rng)

        # THEN
        assert result in ("a", "b")


class TestResolveExpression:
    def test_same_allele_expresses_itself(self) -> None:
        # GIVEN
        alleles = {"a": _allele("a", is_dominant=False)}

        # WHEN
        result = resolve_expression("a", "a", alleles)

        # THEN
        assert result == "a"

    def test_dominant_wins_over_recessive(self) -> None:
        # GIVEN
        alleles = {
            "dom": _allele("dom", is_dominant=True),
            "rec": _allele("rec", is_dominant=False),
        }

        # WHEN
        result = resolve_expression("dom", "rec", alleles)

        # THEN
        assert result == "dom"

    def test_dominant_wins_regardless_of_argument_order(self) -> None:
        # GIVEN
        alleles = {
            "dom": _allele("dom", is_dominant=True),
            "rec": _allele("rec", is_dominant=False),
        }

        # WHEN
        result = resolve_expression("rec", "dom", alleles)

        # THEN
        assert result == "dom"

    def test_two_different_dominants_resolved_randomly(self) -> None:
        # GIVEN
        alleles = {
            "dom1": _allele("dom1", is_dominant=True),
            "dom2": _allele("dom2", is_dominant=True),
        }
        rng = random.Random(3)

        # WHEN
        result = resolve_expression("dom1", "dom2", alleles, rng)

        # THEN
        assert result in ("dom1", "dom2")

    def test_two_different_recessives_resolved_randomly(self) -> None:
        # GIVEN
        alleles = {
            "rec1": _allele("rec1", is_dominant=False),
            "rec2": _allele("rec2", is_dominant=False),
        }
        rng = random.Random(3)

        # WHEN
        result = resolve_expression("rec1", "rec2", alleles, rng)

        # THEN
        assert result in ("rec1", "rec2")

    def test_tie_break_is_roughly_50_50(self) -> None:
        # GIVEN
        alleles = {
            "rec1": _allele("rec1", is_dominant=False),
            "rec2": _allele("rec2", is_dominant=False),
        }
        rng = random.Random(99)
        results = [resolve_expression("rec1", "rec2", alleles, rng) for _ in range(1000)]

        # WHEN
        count_rec1 = results.count("rec1")

        # THEN
        assert 400 < count_rec1 < 600


class TestInheritGenome:
    def test_produces_all_trait_categories(self) -> None:
        # GIVEN
        parent1 = create_baseline_genome()
        parent2 = create_baseline_genome()
        alleles = _full_baseline_allele_lookup()

        # WHEN
        child = inherit_genome(parent1, parent2, None, None, alleles, random.Random(1))

        # THEN
        assert set(child.genes.keys()) == set(TraitCategory)

    def test_baseline_parents_produce_baseline_child(self) -> None:
        # GIVEN
        parent1 = create_baseline_genome()
        parent2 = create_baseline_genome()
        alleles = _full_baseline_allele_lookup()

        # WHEN
        child = inherit_genome(parent1, parent2, None, None, alleles, random.Random(1))

        # THEN
        for trait_category, expected_allele in BASELINE_ALLELES.items():
            assert child.genes[trait_category].expressed_allele == expected_allele

    def test_child_can_inherit_dominant_trait_from_one_parent(self) -> None:
        # GIVEN
        parent1_genes = {
            TraitCategory.EYES: CreatureGene(
                trait_category=TraitCategory.EYES,
                allele_from_parent1="almond_eyes",
                allele_from_parent2="almond_eyes",
                expressed_allele="almond_eyes",
            )
        }
        parent2_genes = {
            TraitCategory.EYES: CreatureGene(
                trait_category=TraitCategory.EYES,
                allele_from_parent1="round_eyes",
                allele_from_parent2="round_eyes",
                expressed_allele="round_eyes",
            )
        }
        parent1 = Genome(genes=parent1_genes)
        parent2 = Genome(genes=parent2_genes)
        alleles = {
            "almond_eyes": _allele("almond_eyes", is_dominant=True),
            "round_eyes": _allele("round_eyes", is_dominant=False),
        }

        # WHEN — only EYES trait exercised here, simulate single-trait genome
        gene1 = parent1.genes[TraitCategory.EYES]
        gene2 = parent2.genes[TraitCategory.EYES]
        from_p1 = transmit_allele(
            (gene1.allele_from_parent1, gene1.allele_from_parent2), None, random.Random(1)
        )
        from_p2 = transmit_allele(
            (gene2.allele_from_parent1, gene2.allele_from_parent2), None, random.Random(1)
        )
        expressed = resolve_expression(from_p1, from_p2, alleles)

        # THEN
        assert from_p1 == "almond_eyes"
        assert from_p2 == "round_eyes"
        assert expressed == "almond_eyes"


def _full_baseline_allele_lookup() -> dict[str, AlleleEntity]:
    return {
        allele_id: _allele(allele_id, is_dominant=False) for allele_id in BASELINE_ALLELES.values()
    }
