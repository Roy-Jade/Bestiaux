import uuid
from dataclasses import dataclass, field
from datetime import datetime

import bcrypt


@dataclass
class UserEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    username: str = ""
    email: str = ""
    password_hash: str = ""
    currency: int = 0
    created_at: datetime | None = None

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), self.password_hash.encode())
