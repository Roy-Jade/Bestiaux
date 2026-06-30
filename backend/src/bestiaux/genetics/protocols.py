import uuid
from typing import Protocol

from bestiaux.genetics.domain import AlleleEntity, Genome


class IAlleleRepository(Protocol):
    async def get_all(self) -> dict[str, AlleleEntity]: ...


class ICreatureGenomeRepository(Protocol):
    async def get_by_creature_id(self, creature_id: uuid.UUID) -> Genome | None: ...

    async def save(self, creature_id: uuid.UUID, genome: Genome) -> None: ...
