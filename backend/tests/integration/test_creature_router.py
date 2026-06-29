from httpx import AsyncClient


async def _register_and_login(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )


class TestCreateCreature:
    async def test_create_returns_201_and_baby(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)

        # WHEN
        response = await client.post("/creature", json={"name": "Blobby"})

        # THEN
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Blobby"
        assert data["life_stage"] == "BABY"
        assert data["is_alive"] is True
        assert data["hunger"] == 100.0

    async def test_create_rejects_duplicate(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)
        await client.post("/creature", json={"name": "Blobby"})

        # WHEN
        response = await client.post("/creature", json={"name": "Another"})

        # THEN
        assert response.status_code == 409

    async def test_create_requires_auth(self, client: AsyncClient) -> None:
        # GIVEN — no login

        # WHEN
        response = await client.post("/creature", json={"name": "Blobby"})

        # THEN
        assert response.status_code == 401


class TestGetActiveCreature:
    async def test_returns_active_creature(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)
        await client.post("/creature", json={"name": "Blobby"})

        # WHEN
        response = await client.get("/creature/active")

        # THEN
        assert response.status_code == 200
        assert response.json()["name"] == "Blobby"

    async def test_returns_404_when_no_creature(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)

        # WHEN
        response = await client.get("/creature/active")

        # THEN
        assert response.status_code == 404


class TestInteract:
    async def test_feed_increases_hunger(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)
        await client.post("/creature", json={"name": "Blobby"})

        # WHEN
        response = await client.post("/creature/interact", json={"action": "feed"})

        # THEN
        assert response.status_code == 200
        assert response.json()["hunger"] == 100.0  # already at max

    async def test_invalid_action_returns_409(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)
        await client.post("/creature", json={"name": "Blobby"})

        # WHEN
        response = await client.post("/creature/interact", json={"action": "dance"})

        # THEN
        assert response.status_code == 409


class TestFreeze:
    async def test_freeze_and_unfreeze(self, client: AsyncClient) -> None:
        # GIVEN
        await _register_and_login(client)
        await client.post("/creature", json={"name": "Blobby"})

        # WHEN
        freeze_response = await client.post("/creature/freeze")

        # THEN
        assert freeze_response.status_code == 200
        assert freeze_response.json()["time_frozen"] is True

        # WHEN
        unfreeze_response = await client.post("/creature/unfreeze")

        # THEN
        assert unfreeze_response.status_code == 200
        assert unfreeze_response.json()["time_frozen"] is False
