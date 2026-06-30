from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.core.dependencies import get_current_user, get_db
from bestiaux.creature.domain import CreatureEntity
from bestiaux.creature.repository import CreatureRepository
from bestiaux.creature.schemas import CreateCreatureRequest, CreatureResponse, InteractRequest
from bestiaux.creature.service import CreatureService
from bestiaux.genetics.repository import AlleleRepository, CreatureGenomeRepository
from bestiaux.genetics.service import GeneticsService
from bestiaux.models.interaction import InteractionType

router = APIRouter(prefix="/creature", tags=["creature"])


def _get_creature_service(db: AsyncSession = Depends(get_db)) -> CreatureService:
    genetics_service = GeneticsService(
        allele_repo=AlleleRepository(session=db),
        genome_repo=CreatureGenomeRepository(session=db),
    )
    return CreatureService(
        creature_repo=CreatureRepository(session=db),
        genome_assigner=genetics_service,
    )


def _to_response(creature: CreatureEntity) -> CreatureResponse:
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


INTERACTION_MAP: dict[str, InteractionType] = {
    "feed": InteractionType.FEED,
    "play": InteractionType.PLAY,
    "heal": InteractionType.HEAL,
}


@router.post("", response_model=CreatureResponse, status_code=201)
async def create_creature(
    body: CreateCreatureRequest,
    user: UserEntity = Depends(get_current_user),
    service: CreatureService = Depends(_get_creature_service),
) -> CreatureResponse:
    creature = await service.create_first_creature(user.id, body.name)
    return _to_response(creature)


@router.get("/active", response_model=CreatureResponse)
async def get_active_creature(
    user: UserEntity = Depends(get_current_user),
    service: CreatureService = Depends(_get_creature_service),
) -> CreatureResponse:
    creature = await service.get_active_creature(user.id)
    return _to_response(creature)


@router.post("/interact", response_model=CreatureResponse)
async def interact(
    body: InteractRequest,
    user: UserEntity = Depends(get_current_user),
    service: CreatureService = Depends(_get_creature_service),
) -> CreatureResponse:
    interaction_type = INTERACTION_MAP.get(body.action)
    if not interaction_type:
        from bestiaux.core.exceptions import ConflictError

        raise ConflictError(f"Invalid action: {body.action}")
    creature = await service.interact(user.id, interaction_type)
    return _to_response(creature)


@router.post("/freeze", response_model=CreatureResponse)
async def freeze(
    user: UserEntity = Depends(get_current_user),
    service: CreatureService = Depends(_get_creature_service),
) -> CreatureResponse:
    creature = await service.freeze(user.id)
    return _to_response(creature)


@router.post("/unfreeze", response_model=CreatureResponse)
async def unfreeze(
    user: UserEntity = Depends(get_current_user),
    service: CreatureService = Depends(_get_creature_service),
) -> CreatureResponse:
    creature = await service.unfreeze(user.id)
    return _to_response(creature)
