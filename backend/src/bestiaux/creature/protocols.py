import uuid
from typing import Protocol

from bestiaux.creature.domain import CreatureEntity


class ICreatureRepository(Protocol):
    async def get_by_id(self, creature_id: uuid.UUID) -> CreatureEntity | None: ...

    async def get_active_for_user(self, user_id: uuid.UUID) -> CreatureEntity | None: ...

    async def create(self, creature: CreatureEntity) -> CreatureEntity: ...

    async def save(self, creature: CreatureEntity) -> None: ...


class IGenomeAssigner(Protocol):
    async def assign_baseline_genome(self, creature_id: uuid.UUID) -> object: ...
