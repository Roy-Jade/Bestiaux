import random
import uuid

from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.genetics.domain import AlleleEntity, CreatureGene, Genome, resolve_expression
from bestiaux.models.genetics import TraitCategory


def are_related(
    ancestors1: set[uuid.UUID],
    ancestors2: set[uuid.UUID],
    parent1_id: uuid.UUID,
    parent2_id: uuid.UUID,
) -> bool:
    """Returns True if the two candidates share any lineage."""
    return parent1_id in ancestors2 or parent2_id in ancestors1 or bool(ancestors1 & ancestors2)


def generate_wild_genome(
    pool_by_category: dict[str, list[str]],
    alleles: dict[str, AlleleEntity],
    rng: random.Random | None = None,
) -> Genome:
    """Generates a random genotype for a virtual wild creature.

    For each trait, two alleles are picked independently from the available
    pool (baseline + player's unlocked alleles). All alleles have equal
    probability — weighting and rarity are intentionally left for future work.
    """
    rng = rng or random
    genes: dict[TraitCategory, CreatureGene] = {}

    for trait_category in TraitCategory:
        available = pool_by_category.get(trait_category.value, [BASELINE_ALLELES[trait_category]])
        allele_a = rng.choice(available)
        allele_b = rng.choice(available)
        expressed = resolve_expression(allele_a, allele_b, alleles, rng)
        genes[trait_category] = CreatureGene(
            trait_category=trait_category,
            allele_from_parent1=allele_a,
            allele_from_parent2=allele_b,
            expressed_allele=expressed,
        )

    return Genome(genes=genes)
