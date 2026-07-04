from datetime import UTC, datetime, timedelta

from bestiaux.models.creature import LifeStage
from bestiaux.models.interaction import TrainTarget
from bestiaux.training.domain import (
    apply_training_to_pending,
    can_train,
    is_informa,
    training_points,
    training_slots_available,
)


class TestTrainingSlotsAvailable:
    def test_no_slots_immediately_after_wake(self) -> None:
        now = datetime.now(UTC)
        assert training_slots_available(now, 0, now) == 0

    def test_one_slot_after_two_hours(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=2)
        assert training_slots_available(woke_up, 0, now) == 1

    def test_five_slots_after_ten_hours(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=10)
        assert training_slots_available(woke_up, 0, now) == 5

    def test_slots_reduced_by_done_today(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=6)
        # 6h / 2h = 3 total slots, 2 already done → 1 available
        assert training_slots_available(woke_up, 2, now) == 1

    def test_never_negative(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=1)
        assert training_slots_available(woke_up, 10, now) == 0


class TestIsInforma:
    def test_informa_when_first_session_done_promptly(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=2, minutes=30)
        assert is_informa(None, woke_up, 0, now)

    def test_not_informa_when_first_session_too_late(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=5)
        assert not is_informa(None, woke_up, 0, now)

    def test_informa_when_previous_session_recent(self) -> None:
        now = datetime.now(UTC)
        last = now - timedelta(hours=3)
        woke_up = now - timedelta(hours=8)
        assert is_informa(last, woke_up, 3, now)

    def test_not_informa_when_previous_session_old(self) -> None:
        now = datetime.now(UTC)
        last = now - timedelta(hours=5)
        woke_up = now - timedelta(hours=8)
        assert not is_informa(last, woke_up, 3, now)


class TestTrainingPoints:
    def test_base_points_when_not_informa(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=6)  # last slot unlocked 4+ hours ago
        last_trained = now - timedelta(hours=4, minutes=1)
        assert training_points(woke_up, 3, last_trained, now) == 4.0

    def test_bonus_when_informa(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=4)
        last_trained = now - timedelta(hours=2, minutes=30)  # within 4h window
        assert training_points(woke_up, 2, last_trained, now) == 5.0


class TestCanTrain:
    def test_adolescent_awake_with_slot_can_train(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=3)
        assert can_train(LifeStage.ADOLESCENT, False, woke_up, 0, now)

    def test_cannot_train_if_asleep(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=3)
        assert not can_train(LifeStage.ADOLESCENT, True, woke_up, 0, now)

    def test_cannot_train_without_slots(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=1)
        assert not can_train(LifeStage.ADOLESCENT, False, woke_up, 0, now)

    def test_baby_cannot_train(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=3)
        assert not can_train(LifeStage.BABY, False, woke_up, 0, now)

    def test_young_adult_can_train(self) -> None:
        now = datetime.now(UTC)
        woke_up = now - timedelta(hours=3)
        assert can_train(LifeStage.YOUNG_ADULT, False, woke_up, 0, now)


class TestApplyTrainingToPending:
    def test_adds_to_force(self) -> None:
        f, b, s = apply_training_to_pending(10.0, 5.0, 3.0, TrainTarget.FORCE, 5.0)
        assert f == 15.0
        assert b == 5.0
        assert s == 3.0

    def test_adds_to_beauty(self) -> None:
        f, b, s = apply_training_to_pending(10.0, 5.0, 3.0, TrainTarget.BEAUTY, 5.0)
        assert f == 10.0
        assert b == 10.0
        assert s == 3.0

    def test_adds_to_size(self) -> None:
        f, b, s = apply_training_to_pending(10.0, 5.0, 3.0, TrainTarget.SIZE, 5.0)
        assert f == 10.0
        assert b == 5.0
        assert s == 8.0
