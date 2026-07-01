from httpx import AsyncClient
from sqlalchemy import select

from bestiaux.models.creature import Creature, LifeStage
from bestiaux.models.genetics import CreatureGenome
from tests.integration.conftest import async_session_test


async def _setup_user_with_adult(client: AsyncClient) -> str:
    """Register a user, create a creature, and force it to ADULT via DB."""
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    create_resp = await client.post("/creature", json={"name": "Parent"})
    creature_id = create_resp.json()["id"]

    async with async_session_test() as session:
        result = await session.execute(select(Creature).where(Creature.id == creature_id))
        creature = result.scalar_one()
        creature.life_stage = LifeStage.ADULT
        creature.is_active = False
        await session.commit()

    return creature_id


class TestBreedWithWild:
    async def test_creates_child_with_genome(self, client: AsyncClient) -> None:
        # GIVEN
        parent_id = await _setup_user_with_adult(client)

        # WHEN
        response = await client.post(
            "/breeding",
            json={
                "parent1": {"type": "creature", "id": parent_id},
                "parent2": {"type": "wild"},
            },
        )

        # THEN
        assert response.status_code == 201
        child_id = response.json()["id"]
        assert response.json()["generation"] == 2

        async with async_session_test() as session:
            genome_result = await session.execute(
                select(CreatureGenome).where(CreatureGenome.creature_id == child_id)
            )
            genes = genome_result.scalars().all()
        assert len(genes) == 5

    async def test_parent_transitions_from_young_adult_to_adult(self, client: AsyncClient) -> None:
        # GIVEN — set parent as YOUNG_ADULT (active)
        await client.post(
            "/auth/register",
            json={"username": "bob", "email": "bob@example.com", "password": "password123"},
        )
        create_resp = await client.post("/creature", json={"name": "YoungAdult"})
        creature_id = create_resp.json()["id"]

        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.life_stage = LifeStage.YOUNG_ADULT
            await session.commit()

        # WHEN
        response = await client.post(
            "/breeding",
            json={
                "parent1": {"type": "creature", "id": creature_id},
                "parent2": {"type": "wild"},
            },
        )

        # THEN
        assert response.status_code == 201
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            parent = result.scalar_one()
        assert parent.life_stage == LifeStage.ADULT
        assert not parent.is_active

    async def test_returns_401_without_auth(self, client: AsyncClient) -> None:
        # GIVEN — no login

        # WHEN
        response = await client.post(
            "/breeding",
            json={
                "parent1": {"type": "creature", "id": "00000000-0000-0000-0000-000000000001"},
                "parent2": {"type": "wild"},
            },
        )

        # THEN
        assert response.status_code == 401
