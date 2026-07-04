from datetime import datetime

from bestiaux.game_constants import (
    TRAINING_BASE_POINTS,
    TRAINING_INFORMA_BONUS,
    TRAINING_INFORMA_WINDOW_HOURS,
    TRAINING_SESSION_COOLDOWN_HOURS,
)
from bestiaux.models.creature import LifeStage
from bestiaux.models.interaction import TrainTarget


def training_slots_available(woke_up_at: datetime, trainings_done_today: int, now: datetime) -> int:
    """Returns how many training sessions are currently available."""
    elapsed_hours = (now - woke_up_at).total_seconds() / 3600
    total_slots = int(elapsed_hours / TRAINING_SESSION_COOLDOWN_HOURS)
    return max(0, total_slots - trainings_done_today)


def is_informa(
    last_trained_at: datetime | None,
    woke_up_at: datetime,
    trainings_done_today: int,
    now: datetime,
) -> bool:
    """Returns True if session is done promptly (within the 'in-forma' window)."""
    reference = last_trained_at if last_trained_at is not None else woke_up_at
    hours_since = (now - reference).total_seconds() / 3600
    return hours_since < TRAINING_INFORMA_WINDOW_HOURS


def training_points(
    woke_up_at: datetime,
    trainings_done_today: int,
    last_trained_at: datetime | None,
    now: datetime,
) -> float:
    """Returns the points earned for a training session."""
    bonus = (
        TRAINING_INFORMA_BONUS
        if is_informa(last_trained_at, woke_up_at, trainings_done_today, now)
        else 0.0
    )
    return TRAINING_BASE_POINTS + bonus


def can_train(
    creature_life_stage: LifeStage,
    is_asleep: bool,
    woke_up_at: datetime | None,
    trainings_done_today: int,
    now: datetime,
) -> bool:
    """Returns True if the creature can train right now."""
    if creature_life_stage not in (LifeStage.ADOLESCENT, LifeStage.YOUNG_ADULT):
        return False
    if is_asleep or woke_up_at is None:
        return False
    return training_slots_available(woke_up_at, trainings_done_today, now) > 0


def apply_training_to_pending(
    pending_force: float,
    pending_beauty: float,
    pending_size: float,
    target: TrainTarget,
    points: float,
) -> tuple[float, float, float]:
    """Adds training points to the appropriate pending buffer."""
    match target:
        case TrainTarget.FORCE:
            return pending_force + points, pending_beauty, pending_size
        case TrainTarget.BEAUTY:
            return pending_force, pending_beauty + points, pending_size
        case TrainTarget.SIZE:
            return pending_force, pending_beauty, pending_size + points
