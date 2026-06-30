from httpx import AsyncClient
from sqlalchemy import select

from bestiaux.game_constants import BASELINE_ALLELES
from bestiaux.models.creature import Creature
from bestiaux.models.genetics import CreatureGenome
from tests.integration.conftest import async_session_test


async def _register_and_create_creature(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    response = await client.post("/creature", json={"name": "Blobby"})
    return response.json()["id"]


class TestCreatureCreationAssignsGenome:
    async def test_creating_creature_assigns_baseline_genome(self, client: AsyncClient) -> None:
        # GIVEN / WHEN
        creature_id = await _register_and_create_creature(client)

        # THEN
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()

            genome_result = await session.execute(
                select(CreatureGenome).where(CreatureGenome.creature_id == creature.id)
            )
            genes = genome_result.scalars().all()

        assert len(genes) == len(BASELINE_ALLELES)
        for gene in genes:
            expected = BASELINE_ALLELES[gene.trait_category]
            assert gene.allele_from_parent1 == expected
            assert gene.allele_from_parent2 == expected
            assert gene.expressed_allele == expected
