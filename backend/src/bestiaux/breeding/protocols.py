import uuid
from typing import Protocol


class IAncestorRepository(Protocol):
    async def get_all_ancestors(self, creature_id: uuid.UUID) -> set[uuid.UUID]: ...
