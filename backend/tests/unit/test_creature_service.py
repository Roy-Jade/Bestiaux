import uuid
from datetime import UTC, datetime

import pytest

from bestiaux.core.exceptions import ConflictError, NotFoundError
from bestiaux.creature.domain import CreatureEntity
from bestiaux.creature.service import CreatureService
from bestiaux.models.creature import LifeStage
from bestiaux.models.interaction import InteractionType


class FakeCreatureRepository:
    def __init__(self, creatures: list[CreatureEntity] | None = None) -> None:
        self.creatures: list[CreatureEntity] = creatures or []

    async def get_by_id(self, creature_id: uuid.UUID) -> CreatureEntity | None:
        return next((c for c in self.creatures if c.id == creature_id), None)

    async def get_active_for_user(self, user_id: uuid.UUID) -> CreatureEntity | None:
        return next(
            (c for c in self.creatures if c.owner_id == user_id and c.is_active),
            None,
        )

    async def create(self, creature: CreatureEntity) -> CreatureEntity:
        self.creatures.append(creature)
        return creature

    async def save(self, creature: CreatureEntity) -> None:
        for i, c in enumerate(self.creatures):
            if c.id == creature.id:
                self.creatures[i] = creature
                return


class FakeGenomeAssigner:
    def __init__(self) -> None:
        self.assigned_for: list[uuid.UUID] = []

    async def assign_baseline_genome(self, creature_id: uuid.UUID) -> object:
        self.assigned_for.append(creature_id)
        return None


class FakeWildPoolUnlocker:
    def __init__(self) -> None:
        self.child_stage_calls: list[uuid.UUID] = []

    async def unlock_for_child_stage(self, creature_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self.child_stage_calls.append(creature_id)


def _make_service(
    repo: FakeCreatureRepository,
) -> CreatureService:
    return CreatureService(
        creature_repo=repo,
        genome_assigner=FakeGenomeAssigner(),
        wild_pool_unlocker=FakeWildPoolUnlocker(),
    )


class TestCreateFirstCreature:
    async def test_creates_baby_creature(self) -> None:
        # GIVEN
        repo = FakeCreatureRepository()
        service = _make_service(repo)
        user_id = uuid.uuid4()

        # WHEN
        creature = await service.create_first_creature(user_id, "Blobby")

        # THEN
        assert creature.name == "Blobby"
        assert creature.life_stage == LifeStage.BABY
        assert creature.generation == 1
        assert creature.owner_id == user_id
        assert creature.is_active
        assert creature.is_alive
        assert len(repo.creatures) == 1

    async def test_rejects_if_already_has_active(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        existing = CreatureEntity(owner_id=user_id, name="Existing", is_active=True)
        repo = FakeCreatureRepository(creatures=[existing])
        service = _make_service(repo)

        # WHEN / THEN
        with pytest.raises(ConflictError, match="Already has an active creature"):
            await service.create_first_creature(user_id, "Another")


class TestGetActiveCreature:
    async def test_returns_creature_with_updated_state(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=user_id,
            name="Blobby",
            hunger=100.0,
            last_interaction_at=now,
            stage_started_at=now,
            is_active=True,
        )
        repo = FakeCreatureRepository(creatures=[creature])
        service = _make_service(repo)

        # WHEN
        result = await service.get_active_creature(user_id)

        # THEN
        assert result.name == "Blobby"

    async def test_raises_if_no_active_creature(self) -> None:
        # GIVEN
        repo = FakeCreatureRepository()
        service = _make_service(repo)

        # WHEN / THEN
        with pytest.raises(NotFoundError, match="No active creature"):
            await service.get_active_creature(uuid.uuid4())


class TestInteract:
    async def test_feed_restores_hunger(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=user_id,
            name="Blobby",
            hunger=50.0,
            last_interaction_at=now,
            stage_started_at=now,
            is_active=True,
        )
        repo = FakeCreatureRepository(creatures=[creature])
        service = _make_service(repo)

        # WHEN
        result = await service.interact(user_id, InteractionType.FEED)

        # THEN
        assert result.hunger > 50.0

    async def test_train_raises_conflict(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=user_id,
            name="Blobby",
            last_interaction_at=now,
            stage_started_at=now,
            is_active=True,
        )
        repo = FakeCreatureRepository(creatures=[creature])
        service = _make_service(repo)

        # WHEN / THEN
        with pytest.raises(ConflictError, match="training endpoint"):
            await service.interact(user_id, InteractionType.TRAIN)


class TestFreeze:
    async def test_freeze_sets_flag(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=user_id,
            name="Blobby",
            last_interaction_at=now,
            stage_started_at=now,
            is_active=True,
        )
        repo = FakeCreatureRepository(creatures=[creature])
        service = _make_service(repo)

        # WHEN
        result = await service.freeze(user_id)

        # THEN
        assert result.time_frozen

    async def test_unfreeze_clears_flag(self) -> None:
        # GIVEN
        user_id = uuid.uuid4()
        now = datetime.now(UTC)
        creature = CreatureEntity(
            owner_id=user_id,
            name="Blobby",
            last_interaction_at=now,
            stage_started_at=now,
            is_active=True,
            time_frozen=True,
            freeze_started_at=now,
        )
        repo = FakeCreatureRepository(creatures=[creature])
        service = _make_service(repo)

        # WHEN
        result = await service.unfreeze(user_id)

        # THEN
        assert not result.time_frozen
