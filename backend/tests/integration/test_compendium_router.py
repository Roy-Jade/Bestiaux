from httpx import AsyncClient
from sqlalchemy import select

from bestiaux.models.biome import Biome
from bestiaux.models.creature import Creature, LifeStage
from tests.integration.conftest import async_session_test


async def _setup_user_with_creature(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    resp = await client.post("/creature", json={"name": "Blobby"})
    return resp.json()["id"]


async def _seed_biome(biome_id: str = "mountain") -> None:
    async with async_session_test() as session:
        existing = await session.execute(select(Biome).where(Biome.id == biome_id))
        if existing.scalar_one_or_none() is None:
            session.add(Biome(id=biome_id, name="Montagnard", description=""))
            await session.commit()


class TestFormsEndpoint:
    async def test_returns_all_possible_forms(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_creature(client)
        await _seed_biome("mountain")

        # WHEN
        response = await client.get("/compendium/forms")

        # THEN
        assert response.status_code == 200
        data = response.json()
        assert "forms" in data
        # 29 forms per biome (1 biome seeded)
        assert len(data["forms"]) == 29

    async def test_discovered_form_shown_correctly(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_creature(client)
        await _seed_biome("mountain")
        creature_id = (await client.get("/creature/active")).json()["id"]

        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.biome_id = "mountain"
            creature.training_force = 77.0
            creature.training_beauty = 35.0
            creature.training_size = 65.0
            await session.commit()

        # WHEN
        response = await client.get("/compendium/forms")

        # THEN
        forms = {f["form_id"]: f for f in response.json()["forms"]}
        assert forms["mountain_3S"]["discovered"] is True
        assert forms["mountain_3S"]["latest_creature_name"] == "Blobby"
        assert forms["mountain_0"]["discovered"] is False

    async def test_requires_auth(self, client: AsyncClient) -> None:
        response = await client.get("/compendium/forms")
        assert response.status_code == 401


class TestHistoryEndpoint:
    async def test_returns_all_creatures(self, client: AsyncClient) -> None:
        # GIVEN
        creature_id = await _setup_user_with_creature(client)

        # WHEN
        response = await client.get("/compendium/history")

        # THEN
        assert response.status_code == 200
        data = response.json()
        assert len(data["creatures"]) == 1
        assert data["creatures"][0]["id"] == creature_id

    async def test_includes_dead_creatures(self, client: AsyncClient) -> None:
        # GIVEN
        creature_id = await _setup_user_with_creature(client)
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.is_alive = False
            creature.is_active = False
            await session.commit()

        # WHEN
        response = await client.get("/compendium/history")

        # THEN
        assert len(response.json()["creatures"]) == 1
        assert response.json()["creatures"][0]["is_alive"] is False


class TestCreatureDetailEndpoint:
    async def test_returns_creature_with_genome(self, client: AsyncClient) -> None:
        # GIVEN
        creature_id = await _setup_user_with_creature(client)

        # WHEN
        response = await client.get(f"/compendium/creature/{creature_id}")

        # THEN
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == creature_id
        assert "genome" in data
        assert len(data["genome"]) == 5  # 5 trait categories

    async def test_returns_404_for_unknown_creature(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_creature(client)

        # WHEN
        response = await client.get("/compendium/creature/00000000-0000-0000-0000-000000000001")

        # THEN
        assert response.status_code == 404


class TestNameAndBiomeEndpoints:
    async def test_set_name(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_creature(client)

        # WHEN
        response = await client.post("/creature/name", json={"name": "Fluffy"})

        # THEN
        assert response.status_code == 200
        assert response.json()["name"] == "Fluffy"

    async def test_set_biome_at_child_stage(self, client: AsyncClient) -> None:
        # GIVEN
        await _seed_biome("mountain")
        creature_id = await _setup_user_with_creature(client)
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.life_stage = LifeStage.CHILD
            await session.commit()

        # WHEN
        response = await client.post("/creature/biome", json={"biome_id": "mountain"})

        # THEN
        assert response.status_code == 200
        assert response.json()["biome_id"] == "mountain"

    async def test_set_biome_rejected_outside_child_stage(self, client: AsyncClient) -> None:
        # GIVEN — creature is BABY
        await _setup_user_with_creature(client)

        # WHEN
        response = await client.post("/creature/biome", json={"biome_id": "mountain"})

        # THEN
        assert response.status_code == 409
