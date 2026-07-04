from bestiaux.models.creature import LifeStage
from bestiaux.models.genetics import TraitCategory

PHASE_DURATIONS_SECONDS: dict[LifeStage, float | None] = {
    LifeStage.BABY: 1 * 60 * 60,  # 1 hour
    LifeStage.CHILD: 2 * 24 * 60 * 60,  # 2 days
    LifeStage.ADOLESCENT: 3 * 24 * 60 * 60,  # 3 days
    LifeStage.YOUNG_ADULT: None,  # infinite, manual transition
    LifeStage.ADULT: None,  # final stage
}

PHASE_ORDER: list[LifeStage] = [
    LifeStage.BABY,
    LifeStage.CHILD,
    LifeStage.ADOLESCENT,
    LifeStage.YOUNG_ADULT,
    LifeStage.ADULT,
]

HUNGER_DECAY_PER_HOUR = 4.0
HEALTH_DECAY_PER_HOUR = 2.0
HAPPINESS_DECAY_PER_HOUR = 3.0

FEED_RESTORE = 30.0
PLAY_RESTORE = 30.0
HEAL_RESTORE = 30.0

AUTONOMY_GAIN_PER_INTERACTION = 0.5

MAX_REPRODUCTIONS = 5

# Daily cycle
MIN_AWAKE_HOURS = 10.0  # minimum awake before player can trigger sleep
AUTO_SLEEP_HOURS = 14.0  # auto-sleep after this many hours awake
MIN_SLEEP_HOURS = 8.0  # minimum sleep before player can trigger wake
AUTO_WAKE_HOURS = 12.0  # auto-wake after this many hours asleep

# Training sessions
TRAINING_SESSION_COOLDOWN_HOURS = 2.0
TRAINING_BASE_POINTS = 4.0
TRAINING_INFORMA_BONUS = 1.0
TRAINING_INFORMA_WINDOW_HOURS = 4.0  # bonus if session done within 4h of last (2h after unlock)

TRAINING_VISUAL_THRESHOLDS: list[int] = [25, 50, 75, 100]

# Mentor
MENTOR_AFFINITY_SAME_BIOME = 0.3
MENTOR_AFFINITY_DIFFERENT_BIOME = 0.1
MIN_MENTOR_CHANGE_HOURS = 24.0  # minimum time before mentor can be changed again

BASELINE_ALLELES: dict[TraitCategory, str] = {
    TraitCategory.EYES: "round_eyes",
    TraitCategory.SKULL_TOP: "no_horn",
    TraitCategory.DORSAL: "no_dorsal",
    TraitCategory.CAUDAL: "no_tail",
    TraitCategory.COLOR: "light_grey",
}
