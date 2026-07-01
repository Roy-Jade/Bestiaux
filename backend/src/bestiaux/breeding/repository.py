import uuid
from collections import deque

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bestiaux.models.creature import Creature


class AncestorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all_ancestors(self, creature_id: uuid.UUID) -> set[uuid.UUID]:
        """BFS traversal of the ancestor tree via parent1_id / parent2_id links."""
        ancestors: set[uuid.UUID] = set()
        queue: deque[uuid.UUID] = deque([creature_id])

        while queue:
            current_id = queue.popleft()
            result = await self.session.execute(
                select(Creature.parent1_id, Creature.parent2_id).where(Creature.id == current_id)
            )
            row = result.one_or_none()
            if row is None:
                continue
            for parent_id in (row.parent1_id, row.parent2_id):
                if parent_id is not None and parent_id not in ancestors:
                    ancestors.add(parent_id)
                    queue.append(parent_id)

        return ancestors
