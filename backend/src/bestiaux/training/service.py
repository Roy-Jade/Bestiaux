import uuid
from datetime import UTC, datetime

from bestiaux.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from bestiaux.creature.domain import CreatureEntity
from bestiaux.game_constants import MIN_MENTOR_CHANGE_HOURS
from bestiaux.models.creature import LifeStage
from bestiaux.models.interaction import TrainTarget
from bestiaux.training.domain import (
    apply_training_to_pending,
    can_train,
    training_points,
)
from bestiaux.training.protocols import ITrainingCreatureRepository


class TrainingService:
    def __init__(self, repo: ITrainingCreatureRepository) -> None:
        self.repo = repo

    async def train(self, user_id: uuid.UUID, target: TrainTarget) -> CreatureEntity:
        creature = await self._get_active_alive(user_id)
        now = datetime.now(UTC)

        if not can_train(
            creature.life_stage,
            creature.is_asleep,
            creature.woke_up_at,
            creature.trainings_done_today,
            now,
        ):
            raise ConflictError("No training session available")

        points = training_points(
            creature.woke_up_at,  # type: ignore[arg-type]
            creature.trainings_done_today,
            creature.last_trained_at,
            now,
        )
        (
            creature.pending_training_force,
            creature.pending_training_beauty,
            creature.pending_training_size,
        ) = apply_training_to_pending(
            creature.pending_training_force,
            creature.pending_training_beauty,
            creature.pending_training_size,
            target,
            points,
        )
        creature.trainings_done_today += 1
        creature.last_trained_at = now
        await self.repo.save(creature)
        return creature

    async def wake_up(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_active_alive(user_id)
        now = datetime.now(UTC)

        if creature.life_stage == LifeStage.BABY:
            raise ConflictError("Baby creatures do not have a sleep cycle")
        if not creature.is_asleep:
            raise ConflictError("Creature is already awake")
        if not creature.can_wake(now):
            raise ConflictError("Creature has not slept long enough yet")

        creature.wake_up(now)
        await self.repo.save(creature)
        return creature

    async def go_to_sleep(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_active_alive(user_id)
        now = datetime.now(UTC)

        if creature.life_stage == LifeStage.BABY:
            raise ConflictError("Baby creatures do not have a sleep cycle")
        if creature.is_asleep:
            raise ConflictError("Creature is already asleep")
        if not creature.can_sleep(now):
            raise ConflictError("Creature has not been awake long enough yet")

        mentor_data = None
        if creature.mentor_id is not None:
            mentor_data = await self.repo.get_mentor_data(creature.mentor_id)

        creature.go_to_sleep(now, mentor_data)
        await self.repo.save(creature)
        return creature

    async def assign_mentor(self, user_id: uuid.UUID, mentor_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_active_alive(user_id)
        now = datetime.now(UTC)

        if creature.life_stage not in (LifeStage.ADOLESCENT, LifeStage.YOUNG_ADULT):
            raise ConflictError("Mentoring is only available from adolescence")

        mentor = await self.repo.get_by_id(mentor_id)
        if mentor is None:
            raise NotFoundError("Mentor not found")
        if mentor.owner_id != user_id:
            raise ForbiddenError("Mentor does not belong to this user")
        if mentor.life_stage != LifeStage.ADULT:
            raise ConflictError("Mentor must be an adult creature")

        if creature.mentor_id is not None and creature.mentor_since is not None:
            hours_since_change = (now - creature.mentor_since).total_seconds() / 3600
            if hours_since_change < MIN_MENTOR_CHANGE_HOURS:
                raise ConflictError("Mentor can only be changed once per 24 hours")

        creature.mentor_id = mentor_id
        creature.mentor_since = now
        await self.repo.save(creature)
        return creature

    async def remove_mentor(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_active_alive(user_id)
        now = datetime.now(UTC)

        if creature.mentor_id is None:
            raise ConflictError("No mentor assigned")
        if creature.mentor_since is not None:
            hours_since = (now - creature.mentor_since).total_seconds() / 3600
            if hours_since < MIN_MENTOR_CHANGE_HOURS:
                raise ConflictError("Mentor can only be changed once per 24 hours")

        creature.mentor_id = None
        creature.mentor_since = None
        await self.repo.save(creature)
        return creature

    async def _get_active_alive(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self.repo.get_active_for_user(user_id)
        if not creature:
            raise NotFoundError("No active creature")
        if not creature.is_alive:
            raise ConflictError("Creature is dead")
        return creature
