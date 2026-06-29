import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.creature.domain import CreatureEntity
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
        db_creature = Creature(
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
        )
        self.session.add(db_creature)
        await self.session.commit()
        await self.session.refresh(db_creature)
        return self._to_entity(db_creature)

    async def save(self, creature: CreatureEntity) -> None:
        result = await self.session.execute(select(Creature).where(Creature.id == creature.id))
        db_creature = result.scalar_one()
        db_creature.name = creature.name
        db_creature.life_stage = creature.life_stage
        db_creature.stage_started_at = creature.stage_started_at
        db_creature.biome_id = creature.biome_id
        db_creature.is_active = creature.is_active
        db_creature.is_alive = creature.is_alive
        db_creature.death_cause = creature.death_cause
        db_creature.max_stage_reached = creature.max_stage_reached
        db_creature.autonomy = creature.autonomy
        db_creature.hunger = creature.hunger
        db_creature.health = creature.health
        db_creature.happiness = creature.happiness
        db_creature.training_force = creature.training_force
        db_creature.training_beauty = creature.training_beauty
        db_creature.training_size = creature.training_size
        db_creature.reproduction_count = creature.reproduction_count
        db_creature.last_interaction_at = creature.last_interaction_at
        db_creature.time_frozen = creature.time_frozen
        db_creature.freeze_started_at = creature.freeze_started_at
        await self.session.commit()

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
            created_at=creature.created_at,
        )
