import uuid

import pytest

from bestiaux.auth.domain import UserEntity
from bestiaux.auth.service import AuthService
from bestiaux.core.exceptions import AuthenticationError, ConflictError


class FakeUserRepository:
    def __init__(self, users: list[UserEntity] | None = None) -> None:
        self.users: list[UserEntity] = users or []

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        return next((u for u in self.users if u.id == user_id), None)

    async def get_by_email(self, email: str) -> UserEntity | None:
        return next((u for u in self.users if u.email == email), None)

    async def get_by_username(self, username: str) -> UserEntity | None:
        return next((u for u in self.users if u.username == username), None)

    async def create(self, user: UserEntity) -> UserEntity:
        self.users.append(user)
        return user


class TestRegister:
    async def test_register_creates_user(self) -> None:
        # GIVEN
        repo = FakeUserRepository()
        service = AuthService(user_repo=repo)

        # WHEN
        user = await service.register("alice", "alice@example.com", "password123")

        # THEN
        assert user.username == "alice"
        assert user.email == "alice@example.com"
        assert user.password_hash != "password123"
        assert len(repo.users) == 1

    async def test_register_hashes_password(self) -> None:
        # GIVEN
        repo = FakeUserRepository()
        service = AuthService(user_repo=repo)

        # WHEN
        user = await service.register("alice", "alice@example.com", "password123")

        # THEN
        assert user.verify_password("password123")
        assert not user.verify_password("wrong")

    async def test_register_rejects_duplicate_email(self) -> None:
        # GIVEN
        existing = UserEntity(username="alice", email="alice@example.com", password_hash="x")
        repo = FakeUserRepository(users=[existing])
        service = AuthService(user_repo=repo)

        # WHEN / THEN
        with pytest.raises(ConflictError, match="Email already registered"):
            await service.register("bob", "alice@example.com", "password123")

    async def test_register_rejects_duplicate_username(self) -> None:
        # GIVEN
        existing = UserEntity(username="alice", email="alice@example.com", password_hash="x")
        repo = FakeUserRepository(users=[existing])
        service = AuthService(user_repo=repo)

        # WHEN / THEN
        with pytest.raises(ConflictError, match="Username already taken"):
            await service.register("alice", "bob@example.com", "password123")


class TestLogin:
    async def test_login_returns_user_on_valid_credentials(self) -> None:
        # GIVEN
        repo = FakeUserRepository()
        service = AuthService(user_repo=repo)
        await service.register("alice", "alice@example.com", "password123")

        # WHEN
        user = await service.login("alice@example.com", "password123")

        # THEN
        assert user.username == "alice"

    async def test_login_rejects_wrong_password(self) -> None:
        # GIVEN
        repo = FakeUserRepository()
        service = AuthService(user_repo=repo)
        await service.register("alice", "alice@example.com", "password123")

        # WHEN / THEN
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await service.login("alice@example.com", "wrong")

    async def test_login_rejects_unknown_email(self) -> None:
        # GIVEN
        repo = FakeUserRepository()
        service = AuthService(user_repo=repo)

        # WHEN / THEN
        with pytest.raises(AuthenticationError, match="Invalid email or password"):
            await service.login("unknown@example.com", "password123")
