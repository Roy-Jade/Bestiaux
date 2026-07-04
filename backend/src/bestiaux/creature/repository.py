import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.creature.domain import CreatureEntity, MentorData
from bestiaux.models.creature import Creature


class CreatureRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, creature_id: uuid.UUID) -> CreatureEntity | None:
        result = await self.session.execute(select(Creature).where(Creature.id == creature_id))
        creature = result.scalar_one_or_none()
        return self._to_entity(creature) if creature else None

    async def get_active_for_user(self, user_id: uuid.UUID) -> CreatureEntity | None:
        result = await self.session.execute(
            select(Creature).where(Creature.owner_id == user_id, Creature.is_active.is_(True))
        )
        creature = result.scalar_one_or_none()
        return self._to_entity(creature) if creature else None

    async def create(self, creature: CreatureEntity) -> CreatureEntity:
        db_creature = Creature(**self._to_db_dict(creature))
        self.session.add(db_creature)
        await self.session.commit()
        await self.session.refresh(db_creature)
        return self._to_entity(db_creature)

    async def save(self, creature: CreatureEntity) -> None:
        result = await self.session.execute(select(Creature).where(Creature.id == creature.id))
        db_creature = result.scalar_one()
        for key, value in self._to_db_dict(creature).items():
            setattr(db_creature, key, value)
        await self.session.commit()

    async def get_mentor_data(self, mentor_id: uuid.UUID) -> MentorData | None:
        result = await self.session.execute(select(Creature).where(Creature.id == mentor_id))
        mentor = result.scalar_one_or_none()
        if mentor is None:
            return None
        return MentorData(
            training_force=mentor.training_force,
            training_beauty=mentor.training_beauty,
            training_size=mentor.training_size,
            autonomy=mentor.autonomy,
            biome_id=mentor.biome_id,
        )

    @staticmethod
    def _to_db_dict(creature: CreatureEntity) -> dict:
        return {
            "id": creature.id,
            "owner_id": creature.owner_id,
            "name": creature.name,
            "life_stage": creature.life_stage,
            "stage_started_at": creature.stage_started_at,
            "biome_id": creature.biome_id,
            "parent1_id": creature.parent1_id,
            "parent2_id": creature.parent2_id,
            "generation": creature.generation,
            "is_active": creature.is_active,
            "is_alive": creature.is_alive,
            "death_cause": creature.death_cause,
            "max_stage_reached": creature.max_stage_reached,
            "autonomy": creature.autonomy,
            "hunger": creature.hunger,
            "health": creature.health,
            "happiness": creature.happiness,
            "training_force": creature.training_force,
            "training_beauty": creature.training_beauty,
            "training_size": creature.training_size,
            "reproduction_count": creature.reproduction_count,
            "last_interaction_at": creature.last_interaction_at,
            "time_frozen": creature.time_frozen,
            "freeze_started_at": creature.freeze_started_at,
            "is_asleep": creature.is_asleep,
            "woke_up_at": creature.woke_up_at,
            "went_to_sleep_at": creature.went_to_sleep_at,
            "trainings_done_today": creature.trainings_done_today,
            "last_trained_at": creature.last_trained_at,
            "pending_training_force": creature.pending_training_force,
            "pending_training_beauty": creature.pending_training_beauty,
            "pending_training_size": creature.pending_training_size,
            "mentor_id": creature.mentor_id,
            "mentor_since": creature.mentor_since,
        }

    @staticmethod
    def _to_entity(creature: Creature) -> CreatureEntity:
        return CreatureEntity(
            id=creature.id,
            owner_id=creature.owner_id,
            name=creature.name,
            life_stage=creature.life_stage,
            stage_started_at=creature.stage_started_at,
            biome_id=creature.biome_id,
            parent1_id=creature.parent1_id,
            parent2_id=creature.parent2_id,
            generation=creature.generation,
            is_active=creature.is_active,
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
            reproduction_count=creature.reproduction_count,
            last_interaction_at=creature.last_interaction_at,
            time_frozen=creature.time_frozen,
            freeze_started_at=creature.freeze_started_at,
            is_asleep=creature.is_asleep,
            woke_up_at=creature.woke_up_at,
            went_to_sleep_at=creature.went_to_sleep_at,
            trainings_done_today=creature.trainings_done_today,
            last_trained_at=creature.last_trained_at,
            pending_training_force=creature.pending_training_force,
            pending_training_beauty=creature.pending_training_beauty,
            pending_training_size=creature.pending_training_size,
            mentor_id=creature.mentor_id,
            mentor_since=creature.mentor_since,
            created_at=creature.created_at,
        )
