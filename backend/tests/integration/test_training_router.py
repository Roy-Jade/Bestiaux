from httpx import AsyncClient
from sqlalchemy import select

from bestiaux.models.creature import Creature, LifeStage
from tests.integration.conftest import async_session_test


async def _setup_user_with_adolescent(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"username": "alice", "email": "alice@example.com", "password": "password123"},
    )
    create_resp = await client.post("/creature", json={"name": "Trainee"})
    creature_id = create_resp.json()["id"]

    async with async_session_test() as session:
        result = await session.execute(select(Creature).where(Creature.id == creature_id))
        creature = result.scalar_one()
        creature.life_stage = LifeStage.ADOLESCENT
        creature.is_asleep = False
        creature.woke_up_at = creature.stage_started_at
        await session.commit()

    return creature_id


async def _setup_user_with_adult_mentor(client: AsyncClient) -> tuple[str, str]:
    """Returns (apprentice_id, mentor_id). Mentor is inserted directly via DB."""
    import uuid
    from datetime import UTC, datetime

    from sqlalchemy import select as sa_select

    from bestiaux.models.creature import Creature
    from bestiaux.models.user import User

    apprentice_id = await _setup_user_with_adolescent(client)

    async with async_session_test() as session:
        result = await session.execute(sa_select(User).where(User.email == "alice@example.com"))
        user = result.scalar_one()
        mentor = Creature(
            id=uuid.uuid4(),
            owner_id=user.id,
            name="Mentor",
            life_stage=LifeStage.ADULT,
            is_active=False,
            is_alive=True,
            training_force=50.0,
            autonomy=100.0,
            stage_started_at=datetime.now(UTC),
            last_interaction_at=datetime.now(UTC),
            woke_up_at=datetime.now(UTC),
        )
        session.add(mentor)
        await session.commit()
        mentor_id = str(mentor.id)

    return apprentice_id, mentor_id


class TestWakeEndpoint:
    async def test_wake_fails_if_already_awake(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_adolescent(client)

        # WHEN
        response = await client.post("/training/wake")

        # THEN
        assert response.status_code == 409

    async def test_wake_after_sleep(self, client: AsyncClient) -> None:
        # GIVEN
        creature_id = await _setup_user_with_adolescent(client)

        from datetime import UTC, datetime, timedelta

        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.is_asleep = True
            creature.went_to_sleep_at = datetime.now(UTC) - timedelta(hours=9)
            await session.commit()

        # WHEN
        response = await client.post("/training/wake")

        # THEN
        assert response.status_code == 200
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
        assert not creature.is_asleep


class TestSleepEndpoint:
    async def test_sleep_requires_10h_awake(self, client: AsyncClient) -> None:
        # GIVEN — creature just woke up (woke_up_at = now)
        await _setup_user_with_adolescent(client)

        # WHEN
        response = await client.post("/training/sleep")

        # THEN
        assert response.status_code == 409

    async def test_sleep_after_10h_awake(self, client: AsyncClient) -> None:
        # GIVEN
        from datetime import UTC, datetime, timedelta

        creature_id = await _setup_user_with_adolescent(client)
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.woke_up_at = datetime.now(UTC) - timedelta(hours=11)
            await session.commit()

        # WHEN
        response = await client.post("/training/sleep")

        # THEN
        assert response.status_code == 200
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
        assert creature.is_asleep


class TestTrainEndpoint:
    async def test_train_requires_slot(self, client: AsyncClient) -> None:
        # GIVEN — woke up just now, no slots yet
        await _setup_user_with_adolescent(client)

        # WHEN
        response = await client.post("/training/train", json={"target": "FORCE"})

        # THEN
        assert response.status_code == 409

    async def test_train_adds_pending_points(self, client: AsyncClient) -> None:
        # GIVEN — woke up 3h ago, 1 slot available
        from datetime import UTC, datetime, timedelta

        creature_id = await _setup_user_with_adolescent(client)
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
            creature.woke_up_at = datetime.now(UTC) - timedelta(hours=3)
            await session.commit()

        # WHEN
        response = await client.post("/training/train", json={"target": "FORCE"})

        # THEN
        assert response.status_code == 200
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == creature_id))
            creature = result.scalar_one()
        assert creature.pending_training_force > 0
        assert creature.trainings_done_today == 1


class TestMentorEndpoint:
    async def test_assign_mentor(self, client: AsyncClient) -> None:
        # GIVEN
        apprentice_id, mentor_id = await _setup_user_with_adult_mentor(client)

        # WHEN
        response = await client.post("/training/mentor", json={"mentor_id": mentor_id})

        # THEN
        assert response.status_code == 200
        async with async_session_test() as session:
            result = await session.execute(select(Creature).where(Creature.id == apprentice_id))
            creature = result.scalar_one()
        assert str(creature.mentor_id) == mentor_id

    async def test_mentor_must_be_adult(self, client: AsyncClient) -> None:
        # GIVEN — try to use the adolescent apprentice itself as mentor
        apprentice_id = await _setup_user_with_adolescent(client)

        # WHEN — apprentice is ADOLESCENT, not ADULT
        response = await client.post("/training/mentor", json={"mentor_id": apprentice_id})

        # THEN
        assert response.status_code == 409


class TestTrainingStatus:
    async def test_status_returns_correct_data(self, client: AsyncClient) -> None:
        # GIVEN
        await _setup_user_with_adolescent(client)

        # WHEN
        response = await client.get("/training/status")

        # THEN
        assert response.status_code == 200
        data = response.json()
        assert "slots_available" in data
        assert "is_asleep" in data
        assert not data["is_asleep"]
