import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: uuid.UUID) -> UserEntity | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def get_by_email(self, email: str) -> UserEntity | None:
        result = await self.session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def get_by_username(self, username: str) -> UserEntity | None:
        result = await self.session.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()
        return self._to_entity(user) if user else None

    async def create(self, user: UserEntity) -> UserEntity:
        db_user = User(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            currency=user.currency,
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return self._to_entity(db_user)

    @staticmethod
    def _to_entity(user: User) -> UserEntity:
        return UserEntity(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            currency=user.currency,
            created_at=user.created_at,
        )
