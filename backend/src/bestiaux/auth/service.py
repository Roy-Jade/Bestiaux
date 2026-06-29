from bestiaux.auth.domain import UserEntity
from bestiaux.auth.protocols import IUserRepository
from bestiaux.core.exceptions import AuthenticationError, ConflictError


class AuthService:
    def __init__(self, user_repo: IUserRepository) -> None:
        self.user_repo = user_repo

    async def register(self, username: str, email: str, password: str) -> UserEntity:
        if await self.user_repo.get_by_email(email):
            raise ConflictError("Email already registered")
        if await self.user_repo.get_by_username(username):
            raise ConflictError("Username already taken")

        user = UserEntity(
            username=username,
            email=email,
            password_hash=UserEntity.hash_password(password),
        )
        return await self.user_repo.create(user)

    async def login(self, email: str, password: str) -> UserEntity:
        user = await self.user_repo.get_by_email(email)
        if not user or not user.verify_password(password):
            raise AuthenticationError("Invalid email or password")
        return user
