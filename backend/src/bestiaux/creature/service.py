import uuid
from datetime import UTC, datetime

from bestiaux.core.exceptions import ConflictError, NotFoundError
from bestiaux.creature.domain import CreatureEntity, MentorData
from bestiaux.creature.protocols import ICreatureRepository, IGenomeAssigner, IWildPoolUnlocker
from bestiaux.game_constants import PHASE_ORDER
from bestiaux.models.creature import LifeStage
from bestiaux.models.interaction import InteractionType


class CreatureService:
    def __init__(
        self,
        creature_repo: ICreatureRepository,
        genome_assigner: IGenomeAssigner,
        wild_pool_unlocker: IWildPoolUnlocker,
    ) -> None:
        self.creature_repo = creature_repo
        self.genome_assigner = genome_assigner
        self.wild_pool_unlocker = wild_pool_unlocker

    async def create_first_creature(self, owner_id: uuid.UUID, name: str) -> CreatureEntity:
        existing = await self.creature_repo.get_active_for_user(owner_id)
        if existing:
            raise ConflictError("Already has an active creature")

        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=owner_id,
            name=name,
            life_stage=LifeStage.BABY,
            stage_started_at=now,
            last_interaction_at=now,
            generation=1,
        )
        created = await self.creature_repo.create(creature)
        await self.genome_assigner.assign_baseline_genome(created.id)
        return created

    async def get_active_creature(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self.creature_repo.get_active_for_user(user_id)
        if not creature:
            raise NotFoundError("No active creature")

        mentor_data: MentorData | None = None
        if creature.mentor_id is not None:
            mentor_data = await self.creature_repo.get_mentor_data(creature.mentor_id)

        previous_stage = creature.life_stage
        now = datetime.now(UTC)
        creature.apply_reconnection(now, mentor=mentor_data)
        await self.creature_repo.save(creature)

        if creature.is_alive and self._crossed_child_stage(previous_stage, creature.life_stage):
            await self.wild_pool_unlocker.unlock_for_child_stage(creature.id, user_id)

        return creature

    async def interact(
        self, user_id: uuid.UUID, interaction_type: InteractionType
    ) -> CreatureEntity:
        creature = await self._get_alive_creature(user_id)

        now = datetime.now(UTC)
        creature.apply_time_decay(now)
        creature.check_death()

        if not creature.is_alive:
            await self.creature_repo.save(creature)
            return creature

        match interaction_type:
            case InteractionType.FEED:
                creature.feed(now)
            case InteractionType.PLAY:
                creature.play(now)
            case InteractionType.HEAL:
                creature.heal(now)
            case InteractionType.TRAIN:
                raise ConflictError("Use the training endpoint for training")

        await self.creature_repo.save(creature)
        return creature

    async def freeze(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_alive_creature(user_id)
        now = datetime.now(UTC)
        creature.apply_time_decay(now)
        creature.freeze(now)
        await self.creature_repo.save(creature)
        return creature

    async def unfreeze(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self._get_alive_creature(user_id)
        now = datetime.now(UTC)
        creature.unfreeze(now)
        await self.creature_repo.save(creature)
        return creature

    async def _get_alive_creature(self, user_id: uuid.UUID) -> CreatureEntity:
        creature = await self.creature_repo.get_active_for_user(user_id)
        if not creature:
            raise NotFoundError("No active creature")
        if not creature.is_alive:
            raise ConflictError("Creature is dead")
        return creature

    @staticmethod
    def _crossed_child_stage(previous: LifeStage, current: LifeStage) -> bool:
        child_index = PHASE_ORDER.index(LifeStage.CHILD)
        return PHASE_ORDER.index(previous) < child_index <= PHASE_ORDER.index(current)
