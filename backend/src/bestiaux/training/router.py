from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.auth.domain import UserEntity
from bestiaux.core.dependencies import get_current_user, get_db
from bestiaux.creature.domain import CreatureEntity
from bestiaux.creature.schemas import CreatureResponse
from bestiaux.training.domain import is_informa, training_slots_available
from bestiaux.training.repository import TrainingCreatureRepository
from bestiaux.training.schemas import AssignMentorRequest, TrainingStatusResponse, TrainRequest
from bestiaux.training.service import TrainingService

router = APIRouter(prefix="/training", tags=["training"])


def _get_training_service(db: AsyncSession = Depends(get_db)) -> TrainingService:
    return TrainingService(repo=TrainingCreatureRepository(session=db))


def _to_creature_response(creature: CreatureEntity) -> CreatureResponse:
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


@router.post("/train", response_model=CreatureResponse)
async def train(
    body: TrainRequest,
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> CreatureResponse:
    creature = await service.train(user.id, body.target)
    return _to_creature_response(creature)


@router.post("/wake", response_model=CreatureResponse)
async def wake_up(
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> CreatureResponse:
    creature = await service.wake_up(user.id)
    return _to_creature_response(creature)


@router.post("/sleep", response_model=CreatureResponse)
async def go_to_sleep(
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> CreatureResponse:
    creature = await service.go_to_sleep(user.id)
    return _to_creature_response(creature)


@router.post("/mentor", response_model=CreatureResponse)
async def assign_mentor(
    body: AssignMentorRequest,
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> CreatureResponse:
    creature = await service.assign_mentor(user.id, body.mentor_id)
    return _to_creature_response(creature)


@router.delete("/mentor", response_model=CreatureResponse)
async def remove_mentor(
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> CreatureResponse:
    creature = await service.remove_mentor(user.id)
    return _to_creature_response(creature)


@router.get("/status", response_model=TrainingStatusResponse)
async def training_status(
    user: UserEntity = Depends(get_current_user),
    service: TrainingService = Depends(_get_training_service),
) -> TrainingStatusResponse:
    from bestiaux.core.exceptions import NotFoundError
    from bestiaux.training.protocols import ITrainingCreatureRepository

    repo: ITrainingCreatureRepository = service.repo
    creature = await repo.get_active_for_user(user.id)
    if creature is None:
        raise NotFoundError("No active creature")

    now = datetime.now(UTC)
    awake = bool(creature.woke_up_at) and not creature.is_asleep
    slots = (
        training_slots_available(creature.woke_up_at, creature.trainings_done_today, now)
        if awake
        else 0
    )
    en_forme = (
        awake
        and slots > 0
        and is_informa(
            creature.last_trained_at,
            creature.woke_up_at,
            creature.trainings_done_today,
            now,  # type: ignore[arg-type]
        )
    )
    return TrainingStatusResponse(
        slots_available=slots,
        trainings_done_today=creature.trainings_done_today,
        last_trained_at=creature.last_trained_at,
        pending_training_force=creature.pending_training_force,
        pending_training_beauty=creature.pending_training_beauty,
        pending_training_size=creature.pending_training_size,
        mentor_id=creature.mentor_id,
        mentor_since=creature.mentor_since,
        is_asleep=creature.is_asleep,
        is_en_forme=en_forme,
        woke_up_at=creature.woke_up_at,
        went_to_sleep_at=creature.went_to_sleep_at,
    )
