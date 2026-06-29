import uuid
from typing import Protocol

from bestiaux.auth.domain import UserEntity


class IUserRepository(Protocol):
    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None: ...

    async def get_by_email(self, email: str) -> UserEntity | None: ...

    async def get_by_username(self, username: str) -> UserEntity | None: ...

    async def create(self, user: UserEntity) -> UserEntity: ...
