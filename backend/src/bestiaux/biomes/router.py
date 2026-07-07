from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.biomes.schemas import BiomeResponse
from bestiaux.core.dependencies import get_current_user, get_db
from bestiaux.models.biome import Biome

router = APIRouter(prefix="/biomes", tags=["biomes"])


@router.get("", response_model=list[BiomeResponse])
async def list_biomes(
    _: object = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BiomeResponse]:
    result = await db.execute(select(Biome).where(Biome.unlocked_by_default.is_(True)))
    biomes = result.scalars().all()
    return [BiomeResponse(id=b.id, name=b.name, description=b.description) for b in biomes]
