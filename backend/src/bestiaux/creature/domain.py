import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from bestiaux.game_constants import (
    AUTO_SLEEP_HOURS,
    AUTO_WAKE_HOURS,
    AUTONOMY_GAIN_PER_INTERACTION,
    FEED_RESTORE,
    HAPPINESS_DECAY_PER_HOUR,
    HEAL_RESTORE,
    HEALTH_DECAY_PER_HOUR,
    HUNGER_DECAY_PER_HOUR,
    MAX_REPRODUCTIONS,
    PHASE_DURATIONS_SECONDS,
    PHASE_ORDER,
    PLAY_RESTORE,
    TRAINING_VISUAL_THRESHOLDS,
)
from bestiaux.models.creature import DeathCause, LifeStage


@dataclass
class MentorData:
    training_force: float
    training_beauty: float
    training_size: float
    autonomy: float
    biome_id: str | None


@dataclass
class CreatureEntity:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    owner_id: uuid.UUID = field(default_factory=uuid.uuid4)
    name: str = ""
    life_stage: LifeStage = LifeStage.BABY
    stage_started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    biome_id: str | None = None
    parent1_id: uuid.UUID | None = None
    parent2_id: uuid.UUID | None = None
    generation: int = 1
    is_active: bool = True
    is_alive: bool = True
    death_cause: DeathCause | None = None
    max_stage_reached: LifeStage = LifeStage.BABY

    autonomy: float = 0.0
    hunger: float = 100.0
    health: float = 100.0
    happiness: float = 100.0

    training_force: float = 0.0
    training_beauty: float = 0.0
    training_size: float = 0.0

    reproduction_count: int = 0
    last_interaction_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    time_frozen: bool = False
    freeze_started_at: datetime | None = None

    # Daily cycle
    is_asleep: bool = False
    woke_up_at: datetime | None = None
    went_to_sleep_at: datetime | None = None

    # Training
    trainings_done_today: int = 0
    last_trained_at: datetime | None = None
    pending_training_force: float = 0.0
    pending_training_beauty: float = 0.0
    pending_training_size: float = 0.0

    # Mentor
    mentor_id: uuid.UUID | None = None
    mentor_since: datetime | None = None

    created_at: datetime | None = None

    # ── Stat decay ────────────────────────────────────────────────────────────

    def apply_time_decay(self, now: datetime) -> None:
        if self.time_frozen or self.is_asleep or not self.is_alive:
            return

        elapsed_hours = (now - self.last_interaction_at).total_seconds() / 3600
        if elapsed_hours <= 0:
            return

        self.hunger = max(0.0, self.hunger - elapsed_hours * HUNGER_DECAY_PER_HOUR)
        self.health = max(0.0, self.health - elapsed_hours * HEALTH_DECAY_PER_HOUR)
        self.happiness = max(0.0, self.happiness - elapsed_hours * HAPPINESS_DECAY_PER_HOUR)

    def check_death(self) -> None:
        if not self.is_alive:
            return
        if self.hunger <= 0:
            self._die(DeathCause.STARVATION)
        elif self.health <= 0:
            self._die(DeathCause.DISEASE)
        elif self.happiness <= 0:
            self._die(DeathCause.ESCAPE)

    # ── Phase transitions ─────────────────────────────────────────────────────

    def check_phase_transition(self, now: datetime) -> bool:
        if not self.is_alive:
            return False

        duration = PHASE_DURATIONS_SECONDS.get(self.life_stage)
        if duration is None:
            return False

        elapsed = (now - self.stage_started_at).total_seconds()
        if elapsed < duration:
            return False

        current_index = PHASE_ORDER.index(self.life_stage)
        next_stage = PHASE_ORDER[current_index + 1]
        self.life_stage = next_stage
        self.stage_started_at += timedelta(seconds=duration)
        if next_stage.value > self.max_stage_reached.value:
            self.max_stage_reached = next_stage

        if next_stage == LifeStage.CHILD:
            self._start_daily_cycle(self.stage_started_at)

        return True

    # ── Freeze (manual player pause) ─────────────────────────────────────────

    def freeze(self, now: datetime) -> None:
        if self.time_frozen or not self.is_alive:
            return
        self.time_frozen = True
        self.freeze_started_at = now

    def unfreeze(self, now: datetime) -> None:
        if not self.time_frozen or self.freeze_started_at is None:
            return
        frozen_duration = now - self.freeze_started_at
        self.stage_started_at += frozen_duration
        self.last_interaction_at += frozen_duration
        self.time_frozen = False
        self.freeze_started_at = None

    # ── Daily cycle ───────────────────────────────────────────────────────────

    def wake_up(self, now: datetime) -> None:
        self.is_asleep = False
        self.woke_up_at = now
        self.last_interaction_at = now  # prevent retroactive decay for sleep time
        self.trainings_done_today = 0

    def go_to_sleep(self, now: datetime, mentor: MentorData | None = None) -> None:
        self._apply_sleep_batch(mentor)
        self.is_asleep = True
        self.went_to_sleep_at = now

    def can_sleep(self, now: datetime) -> bool:
        if self.is_asleep or self.woke_up_at is None or self.life_stage == LifeStage.BABY:
            return False
        return (now - self.woke_up_at).total_seconds() / 3600 >= 10.0

    def can_wake(self, now: datetime) -> bool:
        if not self.is_asleep or self.went_to_sleep_at is None:
            return False
        return (now - self.went_to_sleep_at).total_seconds() / 3600 >= 8.0

    def process_auto_cycle(self, now: datetime, mentor: MentorData | None = None) -> None:
        """Processes any auto-sleep/wake cycles that should have occurred by `now`."""
        if self.life_stage == LifeStage.BABY or not self.is_alive:
            return

        while True:
            if self.is_asleep:
                if self.went_to_sleep_at is None:
                    break
                sleep_duration = (now - self.went_to_sleep_at).total_seconds() / 3600
                if sleep_duration >= AUTO_WAKE_HOURS:
                    wake_at = self.went_to_sleep_at + timedelta(hours=AUTO_WAKE_HOURS)
                    self.wake_up(wake_at)
                else:
                    break
            else:
                if self.woke_up_at is None:
                    break
                awake_duration = (now - self.woke_up_at).total_seconds() / 3600
                if awake_duration >= AUTO_SLEEP_HOURS:
                    sleep_at = self.woke_up_at + timedelta(hours=AUTO_SLEEP_HOURS)
                    self.apply_time_decay(sleep_at)
                    self.check_death()
                    if not self.is_alive:
                        break
                    self.go_to_sleep(sleep_at, mentor)
                else:
                    break

    # ── Sleep batch ───────────────────────────────────────────────────────────

    def apply_mentor_contribution(self, mentor: MentorData) -> None:
        """Applies one day of mentor training contribution to pending buffers."""
        from math import ceil

        from bestiaux.game_constants import (
            MENTOR_AFFINITY_DIFFERENT_BIOME,
            MENTOR_AFFINITY_SAME_BIOME,
        )

        affinity = (
            MENTOR_AFFINITY_SAME_BIOME
            if mentor.biome_id == self.biome_id
            else MENTOR_AFFINITY_DIFFERENT_BIOME
        )
        autonomy_ratio = mentor.autonomy / 100.0

        self.pending_training_force += ceil(mentor.training_force * affinity * autonomy_ratio)
        self.pending_training_beauty += ceil(mentor.training_beauty * affinity * autonomy_ratio)
        self.pending_training_size += ceil(mentor.training_size * affinity * autonomy_ratio)

    def _apply_sleep_batch(self, mentor: MentorData | None) -> None:
        """Flushes pending training points (+ one day of mentor) into actual stats."""
        if mentor is not None:
            self.apply_mentor_contribution(mentor)

        self.training_force = self._apply_ya_cap(
            self.training_force, self.training_force + self.pending_training_force
        )
        self.training_beauty = self._apply_ya_cap(
            self.training_beauty, self.training_beauty + self.pending_training_beauty
        )
        self.training_size = self._apply_ya_cap(
            self.training_size, self.training_size + self.pending_training_size
        )
        self.pending_training_force = 0.0
        self.pending_training_beauty = 0.0
        self.pending_training_size = 0.0

    def _apply_ya_cap(self, current_stat: float, new_value: float) -> float:
        """In YOUNG_ADULT, stat cannot cross the next visual threshold above its current value."""
        capped = min(100.0, new_value)
        if self.life_stage != LifeStage.YOUNG_ADULT:
            return capped
        next_threshold = next((t for t in TRAINING_VISUAL_THRESHOLDS if t > current_stat), None)
        if next_threshold is None:
            return capped
        return min(capped, float(next_threshold - 1))

    # ── Basic interactions ────────────────────────────────────────────────────

    def feed(self, now: datetime) -> None:
        self._interact(now)
        self.hunger = min(100.0, self.hunger + FEED_RESTORE)

    def play(self, now: datetime) -> None:
        self._interact(now)
        self.happiness = min(100.0, self.happiness + PLAY_RESTORE)

    def heal(self, now: datetime) -> None:
        self._interact(now)
        self.health = min(100.0, self.health + HEAL_RESTORE)

    def can_reproduce(self) -> bool:
        return (
            self.is_alive
            and self.life_stage in (LifeStage.YOUNG_ADULT, LifeStage.ADULT)
            and self.reproduction_count < MAX_REPRODUCTIONS
        )

    # ── Reconnection ─────────────────────────────────────────────────────────

    def apply_reconnection(self, now: datetime, mentor: MentorData | None = None) -> None:
        self.apply_time_decay(now)
        self.check_death()
        while self.is_alive and self.check_phase_transition(now):
            pass
        if self.is_alive:
            self.process_auto_cycle(now, mentor)

    # ── Private ───────────────────────────────────────────────────────────────

    def _interact(self, now: datetime) -> None:
        self.last_interaction_at = now
        self.autonomy = min(100.0, self.autonomy + AUTONOMY_GAIN_PER_INTERACTION)

    def _die(self, cause: DeathCause) -> None:
        self.is_alive = False
        self.is_active = False
        self.death_cause = cause

    def _start_daily_cycle(self, now: datetime) -> None:
        self.woke_up_at = now
        self.is_asleep = False
        self.trainings_done_today = 0
