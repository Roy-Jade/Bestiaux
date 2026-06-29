import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from bestiaux.game_constants import (
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
)
from bestiaux.models.creature import DeathCause, LifeStage


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
    created_at: datetime | None = None

    def apply_time_decay(self, now: datetime) -> None:
        if self.time_frozen or not self.is_alive:
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
        return True

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

    def apply_reconnection(self, now: datetime) -> None:
        self.apply_time_decay(now)
        self.check_death()
        while self.is_alive and self.check_phase_transition(now):
            pass

    def _interact(self, now: datetime) -> None:
        self.last_interaction_at = now
        self.autonomy = min(100.0, self.autonomy + AUTONOMY_GAIN_PER_INTERACTION)

    def _die(self, cause: DeathCause) -> None:
        self.is_alive = False
        self.is_active = False
        self.death_cause = cause
