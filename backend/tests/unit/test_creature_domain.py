from datetime import UTC, datetime, timedelta

from bestiaux.creature.domain import CreatureEntity
from bestiaux.models.creature import DeathCause, LifeStage


def _make_creature(**kwargs) -> CreatureEntity:
    now = datetime.now(UTC)
    defaults = {"stage_started_at": now, "last_interaction_at": now}
    defaults.update(kwargs)
    return CreatureEntity(**defaults)


class TestTimeDecay:
    def test_hunger_decreases_over_time(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(last_interaction_at=now - timedelta(hours=5))

        # WHEN
        creature.apply_time_decay(now)

        # THEN
        assert creature.hunger < 100.0
        assert creature.hunger == 100.0 - 5 * 4.0  # HUNGER_DECAY_PER_HOUR = 4.0

    def test_stats_dont_go_below_zero(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(last_interaction_at=now - timedelta(hours=100))

        # WHEN
        creature.apply_time_decay(now)

        # THEN
        assert creature.hunger == 0.0
        assert creature.health == 0.0
        assert creature.happiness == 0.0

    def test_no_decay_when_frozen(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            last_interaction_at=now - timedelta(hours=10),
            time_frozen=True,
        )

        # WHEN
        creature.apply_time_decay(now)

        # THEN
        assert creature.hunger == 100.0

    def test_no_decay_when_dead(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            last_interaction_at=now - timedelta(hours=10),
            is_alive=False,
        )

        # WHEN
        creature.apply_time_decay(now)

        # THEN
        assert creature.hunger == 100.0


class TestDeath:
    def test_starvation_when_hunger_zero(self) -> None:
        # GIVEN
        creature = _make_creature(hunger=0.0)

        # WHEN
        creature.check_death()

        # THEN
        assert not creature.is_alive
        assert creature.death_cause == DeathCause.STARVATION

    def test_disease_when_health_zero(self) -> None:
        # GIVEN
        creature = _make_creature(health=0.0)

        # WHEN
        creature.check_death()

        # THEN
        assert not creature.is_alive
        assert creature.death_cause == DeathCause.DISEASE

    def test_escape_when_happiness_zero(self) -> None:
        # GIVEN
        creature = _make_creature(happiness=0.0)

        # WHEN
        creature.check_death()

        # THEN
        assert not creature.is_alive
        assert creature.death_cause == DeathCause.ESCAPE

    def test_death_deactivates_creature(self) -> None:
        # GIVEN
        creature = _make_creature(hunger=0.0)

        # WHEN
        creature.check_death()

        # THEN
        assert not creature.is_active


class TestPhaseTransition:
    def test_baby_to_child_after_one_hour(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            life_stage=LifeStage.BABY,
            stage_started_at=now - timedelta(hours=1, seconds=1),
        )

        # WHEN
        transitioned = creature.check_phase_transition(now)

        # THEN
        assert transitioned
        assert creature.life_stage == LifeStage.CHILD

    def test_no_transition_before_duration(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            life_stage=LifeStage.BABY,
            stage_started_at=now - timedelta(minutes=30),
        )

        # WHEN
        transitioned = creature.check_phase_transition(now)

        # THEN
        assert not transitioned
        assert creature.life_stage == LifeStage.BABY

    def test_young_adult_never_transitions_automatically(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            life_stage=LifeStage.YOUNG_ADULT,
            stage_started_at=now - timedelta(days=365),
        )

        # WHEN
        transitioned = creature.check_phase_transition(now)

        # THEN
        assert not transitioned
        assert creature.life_stage == LifeStage.YOUNG_ADULT

    def test_max_stage_reached_updates(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(
            life_stage=LifeStage.BABY,
            stage_started_at=now - timedelta(hours=2),
            max_stage_reached=LifeStage.BABY,
        )

        # WHEN
        creature.check_phase_transition(now)

        # THEN
        assert creature.max_stage_reached == LifeStage.CHILD

    def test_reconnection_chains_multiple_transitions(self) -> None:
        # GIVEN — enough time for baby (1h) + child (2d) + adolescent (3d)
        now = datetime.now(UTC)
        creature = _make_creature(
            life_stage=LifeStage.BABY,
            stage_started_at=now - timedelta(days=10),
            last_interaction_at=now,  # high stats to avoid death
        )

        # WHEN
        creature.apply_reconnection(now)

        # THEN
        assert creature.life_stage == LifeStage.YOUNG_ADULT


class TestFreeze:
    def test_freeze_sets_flag_and_timestamp(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature()

        # WHEN
        creature.freeze(now)

        # THEN
        assert creature.time_frozen
        assert creature.freeze_started_at == now

    def test_unfreeze_shifts_timestamps(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        freeze_time = now - timedelta(days=3)
        creature = _make_creature(
            stage_started_at=now - timedelta(days=5),
            last_interaction_at=now - timedelta(days=5),
            time_frozen=True,
            freeze_started_at=freeze_time,
        )
        original_stage_start = creature.stage_started_at
        original_last_interaction = creature.last_interaction_at

        # WHEN
        creature.unfreeze(now)

        # THEN
        frozen_duration = now - freeze_time
        assert creature.stage_started_at == original_stage_start + frozen_duration
        assert creature.last_interaction_at == original_last_interaction + frozen_duration
        assert not creature.time_frozen
        assert creature.freeze_started_at is None

    def test_freeze_does_nothing_if_already_frozen(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        original_freeze = now - timedelta(hours=1)
        creature = _make_creature(time_frozen=True, freeze_started_at=original_freeze)

        # WHEN
        creature.freeze(now)

        # THEN
        assert creature.freeze_started_at == original_freeze


class TestInteractions:
    def test_feed_restores_hunger(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(hunger=50.0)

        # WHEN
        creature.feed(now)

        # THEN
        assert creature.hunger == 80.0

    def test_play_restores_happiness(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(happiness=50.0)

        # WHEN
        creature.play(now)

        # THEN
        assert creature.happiness == 80.0

    def test_heal_restores_health(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(health=50.0)

        # WHEN
        creature.heal(now)

        # THEN
        assert creature.health == 80.0

    def test_stats_cap_at_100(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(hunger=90.0)

        # WHEN
        creature.feed(now)

        # THEN
        assert creature.hunger == 100.0

    def test_interaction_increases_autonomy(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(autonomy=0.0)

        # WHEN
        creature.feed(now)

        # THEN
        assert creature.autonomy == 0.5

    def test_interaction_updates_last_interaction_at(self) -> None:
        # GIVEN
        now = datetime.now(UTC)
        creature = _make_creature(last_interaction_at=now - timedelta(hours=1))

        # WHEN
        creature.feed(now)

        # THEN
        assert creature.last_interaction_at == now


class TestCanReproduce:
    def test_young_adult_can_reproduce(self) -> None:
        creature = _make_creature(life_stage=LifeStage.YOUNG_ADULT)
        assert creature.can_reproduce()

    def test_adult_can_reproduce(self) -> None:
        creature = _make_creature(life_stage=LifeStage.ADULT)
        assert creature.can_reproduce()

    def test_child_cannot_reproduce(self) -> None:
        creature = _make_creature(life_stage=LifeStage.CHILD)
        assert not creature.can_reproduce()

    def test_cannot_reproduce_at_max(self) -> None:
        creature = _make_creature(life_stage=LifeStage.ADULT, reproduction_count=5)
        assert not creature.can_reproduce()

    def test_dead_cannot_reproduce(self) -> None:
        creature = _make_creature(life_stage=LifeStage.ADULT, is_alive=False)
        assert not creature.can_reproduce()
