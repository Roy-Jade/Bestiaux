import uuid
from typing import Protocol

from bestiaux.creature.domain import CreatureEntity, MentorData


class ICreatureRepository(Protocol):
    async def get_by_id(self, creature_id: uuid.UUID) -> CreatureEntity | None: ...

    async def get_active_for_user(self, user_id: uuid.UUID) -> CreatureEntity | None: ...

    async def create(self, creature: CreatureEntity) -> CreatureEntity: ...

    async def save(self, creature: CreatureEntity) -> None: ...

    async def get_mentor_data(self, mentor_id: uuid.UUID) -> MentorData | None: ...


class IGenomeAssigner(Protocol):
    async def assign_baseline_genome(self, creature_id: uuid.UUID) -> object: ...


class IWildPoolUnlocker(Protocol):
    async def unlock_for_child_stage(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None: ...
