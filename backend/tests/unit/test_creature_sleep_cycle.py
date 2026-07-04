from datetime import UTC, datetime, timedelta

from bestiaux.creature.domain import CreatureEntity, MentorData
from bestiaux.models.creature import LifeStage


def _awake_adolescent(woke_up_hours_ago: float = 0.0) -> CreatureEntity:
    now = datetime.now(UTC)
    woke_at = now - timedelta(hours=woke_up_hours_ago)
    return CreatureEntity(
        life_stage=LifeStage.ADOLESCENT,
        is_asleep=False,
        is_alive=True,
        woke_up_at=woke_at,
        last_interaction_at=woke_at,
        stage_started_at=now - timedelta(days=1),
        trainings_done_today=0,
    )


class TestSleepWake:
    def test_can_sleep_after_ten_hours(self) -> None:
        creature = _awake_adolescent(woke_up_hours_ago=10.0)
        now = datetime.now(UTC)  # captured after creature so now > woke_up_at + 10h
        assert creature.can_sleep(now)

    def test_cannot_sleep_before_ten_hours(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=9.0)
        assert not creature.can_sleep(now)

    def test_wake_up_resets_training_counter(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.ADOLESCENT,
            is_asleep=True,
            is_alive=True,
            went_to_sleep_at=now - timedelta(hours=9),
            trainings_done_today=3,
        )
        creature.wake_up(now)
        assert creature.trainings_done_today == 0
        assert not creature.is_asleep

    def test_wake_up_sets_last_interaction(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.ADOLESCENT,
            is_asleep=True,
            is_alive=True,
            went_to_sleep_at=now - timedelta(hours=9),
            last_interaction_at=now - timedelta(hours=20),
        )
        creature.wake_up(now)
        assert creature.last_interaction_at == now

    def test_go_to_sleep_sets_flag(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=11.0)
        creature.go_to_sleep(now)
        assert creature.is_asleep
        assert creature.went_to_sleep_at == now

    def test_stats_do_not_decay_while_asleep(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.ADOLESCENT,
            is_asleep=True,
            is_alive=True,
            hunger=80.0,
            last_interaction_at=now - timedelta(hours=5),
        )
        creature.apply_time_decay(now)
        assert creature.hunger == 80.0


class TestAutoSleepCycle:
    def test_auto_sleep_after_14h(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=15.0)
        creature.process_auto_cycle(now)
        assert creature.is_asleep

    def test_auto_wake_after_12h_sleep(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.ADOLESCENT,
            is_asleep=True,
            is_alive=True,
            went_to_sleep_at=now - timedelta(hours=13),
            last_interaction_at=now - timedelta(hours=13),
        )
        creature.process_auto_cycle(now)
        assert not creature.is_asleep

    def test_baby_skips_auto_cycle(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.BABY,
            is_asleep=False,
            is_alive=True,
            woke_up_at=now - timedelta(hours=20),
        )
        creature.process_auto_cycle(now)
        assert not creature.is_asleep  # no change


class TestSleepBatch:
    def test_pending_points_applied_at_sleep(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=11.0)
        creature.pending_training_force = 10.0
        creature.pending_training_beauty = 5.0
        creature.go_to_sleep(now)
        assert creature.training_force == 10.0
        assert creature.training_beauty == 5.0
        assert creature.pending_training_force == 0.0

    def test_mentor_contribution_applied_at_sleep(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=11.0)
        creature.biome_id = "mountain"
        mentor = MentorData(
            training_force=100.0,
            training_beauty=100.0,
            training_size=100.0,
            autonomy=100.0,
            biome_id="mountain",
        )
        creature.go_to_sleep(now, mentor)
        # ceil(100 * 0.3 * 1.0) = 30 per stat
        assert creature.training_force == 30.0

    def test_ya_cap_prevents_threshold_crossing(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.YOUNG_ADULT,
            is_asleep=False,
            is_alive=True,
            training_force=25.0,  # crossed threshold 1
            pending_training_force=30.0,  # would bring it to 55, crossing threshold 2
            woke_up_at=now - timedelta(hours=11),
        )
        creature.go_to_sleep(now)
        # Cap = next threshold above 25 - 1 = 50 - 1 = 49
        assert creature.training_force == 49.0

    def test_ya_cap_when_no_threshold_crossed(self) -> None:
        now = datetime.now(UTC)
        creature = CreatureEntity(
            life_stage=LifeStage.YOUNG_ADULT,
            is_asleep=False,
            is_alive=True,
            training_force=20.0,  # below first threshold (25)
            pending_training_force=10.0,  # would bring to 30
            woke_up_at=now - timedelta(hours=11),
        )
        creature.go_to_sleep(now)
        # Cap = next threshold above 20 - 1 = 25 - 1 = 24
        assert creature.training_force == 24.0

    def test_stats_capped_at_100(self) -> None:
        now = datetime.now(UTC)
        creature = _awake_adolescent(woke_up_hours_ago=11.0)
        creature.training_force = 90.0
        creature.pending_training_force = 50.0
        creature.go_to_sleep(now)
        assert creature.training_force == 100.0
