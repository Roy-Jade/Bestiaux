import uuid

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.auth.repository import UserRepository
from bestiaux.database import get_db


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> UserEntity:
    user_id_str = request.session.get("user_id")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Not authenticated")

    repo = UserRepository(session=db)
    user = await repo.get_by_id(uuid.UUID(user_id_str))
    if not user:
        request.session.clear()
        raise HTTPException(status_code=401, detail="User not found")

    return user
