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

TRAINING_VISUAL_THRESHOLDS = [25, 50, 75, 100]

BASELINE_ALLELES: dict[TraitCategory, str] = {
    TraitCategory.EYES: "round_eyes",
    TraitCategory.SKULL_TOP: "no_horn",
    TraitCategory.DORSAL: "no_dorsal",
    TraitCategory.CAUDAL: "no_tail",
    TraitCategory.COLOR: "light_grey",
}
