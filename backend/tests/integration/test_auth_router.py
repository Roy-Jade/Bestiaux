from httpx import AsyncClient


class TestRegisterEndpoint:
    async def test_register_returns_201_and_user(self, client: AsyncClient) -> None:
        # GIVEN
        payload = {"username": "alice", "email": "alice@example.com", "password": "password123"}

        # WHEN
        response = await client.post("/auth/register", json=payload)

        # THEN
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "alice"
        assert data["email"] == "alice@example.com"
        assert "password" not in data
        assert "password_hash" not in data

    async def test_register_sets_session_cookie(self, client: AsyncClient) -> None:
        # GIVEN
        payload = {"username": "alice", "email": "alice@example.com", "password": "password123"}

        # WHEN
        response = await client.post("/auth/register", json=payload)

        # THEN
        assert "session" in response.cookies

    async def test_register_rejects_duplicate_email(self, client: AsyncClient) -> None:
        # GIVEN
        payload = {"username": "alice", "email": "alice@example.com", "password": "password123"}
        await client.post("/auth/register", json=payload)

        # WHEN
        response = await client.post(
            "/auth/register",
            json={"username": "bob", "email": "alice@example.com", "password": "password456"},
        )

        # THEN
        assert response.status_code == 409


class TestLoginEndpoint:
    async def test_login_returns_user(self, client: AsyncClient) -> None:
        # GIVEN
        await client.post(
            "/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

        # WHEN
        response = await client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "password123"},
        )

        # THEN
        assert response.status_code == 200
        assert response.json()["username"] == "alice"

    async def test_login_rejects_wrong_password(self, client: AsyncClient) -> None:
        # GIVEN
        await client.post(
            "/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

        # WHEN
        response = await client.post(
            "/auth/login",
            json={"email": "alice@example.com", "password": "wrong"},
        )

        # THEN
        assert response.status_code == 401


class TestMeEndpoint:
    async def test_me_returns_user_when_authenticated(self, client: AsyncClient) -> None:
        # GIVEN
        await client.post(
            "/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

        # WHEN
        response = await client.get("/auth/me")

        # THEN
        assert response.status_code == 200
        assert response.json()["username"] == "alice"

    async def test_me_returns_401_when_not_authenticated(self, client: AsyncClient) -> None:
        # GIVEN — no login

        # WHEN
        response = await client.get("/auth/me")

        # THEN
        assert response.status_code == 401


class TestLogoutEndpoint:
    async def test_logout_clears_session(self, client: AsyncClient) -> None:
        # GIVEN
        await client.post(
            "/auth/register",
            json={"username": "alice", "email": "alice@example.com", "password": "password123"},
        )

        # WHEN
        await client.post("/auth/logout")
        response = await client.get("/auth/me")

        # THEN
        assert response.status_code == 401
