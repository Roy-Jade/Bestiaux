import random
from dataclasses import dataclass

from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.models.genetics import TraitCategory


@dataclass(frozen=True)
class AlleleEntity:
    id: str
    trait_category: TraitCategory
    name: str
    is_dominant: bool
    sprite_key: str
    biome_id: str | None = None


@dataclass
class CreatureGene:
    trait_category: TraitCategory
    allele_from_parent1: str
    allele_from_parent2: str
    expressed_allele: str


@dataclass
class Genome:
    genes: dict[TraitCategory, CreatureGene]


def create_baseline_genome() -> Genome:
    genes = {
        trait_category: CreatureGene(
            trait_category=trait_category,
            allele_from_parent1=allele_id,
            allele_from_parent2=allele_id,
            expressed_allele=allele_id,
        )
        for trait_category, allele_id in BASELINE_ALLELES.items()
    }
    return Genome(genes=genes)


def select_allele(
    parent_alleles: tuple[str, str], rng: random.Random | None = None
) -> tuple[str, str]:
    """Flags one of the parent's two alleles for transmission.

    Returns (selected, other) — the parent's full pair is preserved so the
    mutation step can consider both (e.g. for future trait-evolution mutations).
    """
    rng = rng or random
    a, b = parent_alleles
    return (a, b) if rng.random() < 0.5 else (b, a)


def apply_mutation(selected_allele: str, other_allele: str, biome_id: str | None) -> str:
    """V1 stub: no mutation, transmits the selected allele unchanged.

    Future versions will use other_allele and biome_id to decide whether a
    biome-linked mutation replaces the selected allele.
    """
    return selected_allele


def transmit_allele(
    parent_alleles: tuple[str, str],
    biome_id: str | None,
    rng: random.Random | None = None,
) -> str:
    selected, other = select_allele(parent_alleles, rng)
    return apply_mutation(selected, other, biome_id)


def resolve_expression(
    allele_a_id: str,
    allele_b_id: str,
    alleles: dict[str, AlleleEntity],
    rng: random.Random | None = None,
) -> str:
    if allele_a_id == allele_b_id:
        return allele_a_id

    rng = rng or random
    allele_a = alleles[allele_a_id]
    allele_b = alleles[allele_b_id]

    if allele_a.is_dominant != allele_b.is_dominant:
        return allele_a_id if allele_a.is_dominant else allele_b_id

    return allele_a_id if rng.random() < 0.5 else allele_b_id


def inherit_genome(
    parent1_genome: Genome,
    parent2_genome: Genome,
    parent1_biome_id: str | None,
    parent2_biome_id: str | None,
    alleles: dict[str, AlleleEntity],
    rng: random.Random | None = None,
) -> Genome:
    genes = {}
    for trait_category in TraitCategory:
        gene1 = parent1_genome.genes[trait_category]
        gene2 = parent2_genome.genes[trait_category]

        from_parent1 = transmit_allele(
            (gene1.allele_from_parent1, gene1.allele_from_parent2), parent1_biome_id, rng
        )
        from_parent2 = transmit_allele(
            (gene2.allele_from_parent1, gene2.allele_from_parent2), parent2_biome_id, rng
        )
        expressed = resolve_expression(from_parent1, from_parent2, alleles, rng)

        genes[trait_category] = CreatureGene(
            trait_category=trait_category,
            allele_from_parent1=from_parent1,
            allele_from_parent2=from_parent2,
            expressed_allele=expressed,
        )
    return Genome(genes=genes)
