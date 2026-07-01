from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.breeding.repository import AncestorRepository
from bestiaux.breeding.schemas import BreedingRequest, OwnedParent, WildParent
from bestiaux.breeding.service import BreedingService
from bestiaux.core.dependencies import get_current_user, get_db
from bestiaux.core.exceptions import ConflictError
from bestiaux.creature.repository import CreatureRepository
from bestiaux.creature.schemas import CreatureResponse
from bestiaux.genetics.repository import (
    AlleleRepository,
    CreatureGenomeRepository,
    WildPoolRepository,
)

router = APIRouter(prefix="/breeding", tags=["breeding"])


def _get_breeding_service(db: AsyncSession = Depends(get_db)) -> BreedingService:
    return BreedingService(
        creature_repo=CreatureRepository(session=db),
        ancestor_repo=AncestorRepository(session=db),
        allele_repo=AlleleRepository(session=db),
        genome_repo=CreatureGenomeRepository(session=db),
        pool_repo=WildPoolRepository(session=db),
    )


def _to_response(creature) -> CreatureResponse:
    return CreatureResponse(
        id=creature.id,
        name=creature.name,
        life_stage=creature.life_stage,
        biome_id=creature.biome_id,
        generation=creature.generation,
        is_alive=creature.is_alive,
        death_cause=creature.death_cause,
        max_stage_reached=creature.max_stage_reached,
        autonomy=creature.autonomy,
        hunger=creature.hunger,
        health=creature.health,
        happiness=creature.happiness,
        training_force=creature.training_force,
        training_beauty=creature.training_beauty,
        training_size=creature.training_size,
        time_frozen=creature.time_frozen,
        created_at=creature.created_at,
    )


@router.post("", response_model=CreatureResponse, status_code=201)
async def breed(
    body: BreedingRequest,
    user: UserEntity = Depends(get_current_user),
    service: BreedingService = Depends(_get_breeding_service),
) -> CreatureResponse:
    match (body.parent1, body.parent2):
        case (OwnedParent() as p1, OwnedParent() as p2):
            child = await service.breed_owned(user.id, p1.id, p2.id)
        case (OwnedParent() as p1, WildParent()):
            child = await service.breed_with_wild(user.id, p1.id)
        case (WildParent(), OwnedParent() as p2):
            child = await service.breed_with_wild(user.id, p2.id)
        case _:
            raise ConflictError("At least one parent must be an owned creature")
    return _to_response(child)
