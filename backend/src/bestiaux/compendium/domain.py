from bestiaux.game_constants import TRAINING_VISUAL_THRESHOLDS

_SORTED_LETTERS = ["B", "S", "W"]


def compute_form_id(
    biome_id: str,
    training_force: float,
    training_beauty: float,
    training_size: float,
) -> str:
    """Derives the visual form ID from biome and training stats.

    Only the highest threshold level reached (across all three stats) matters.
    If multiple stats share that maximum level, all appear in the ID.

    Examples:
      force=77 (T3), beauty=35 (T1), size=65 (T2) => max=3, only S => "mountain_3S"
      force=58 (T2), beauty=67 (T2), size=44 (T1) => max=2, B+S => "mountain_2BS"
      force=0, beauty=0, size=0                   => max=0, none  => "mountain_0"
    """
    levels = {
        "S": _threshold_level(training_force),
        "B": _threshold_level(training_beauty),
        "W": _threshold_level(training_size),
    }
    max_level = max(levels.values())
    if max_level == 0:
        return f"{biome_id}_0"

    dominant = "".join(letter for letter in _SORTED_LETTERS if levels[letter] == max_level)
    return f"{biome_id}_{max_level}{dominant}"


def all_possible_form_ids(biome_ids: list[str]) -> list[str]:
    """Returns every possible form ID for the given biomes.

    29 forms per biome: 1 base + 4 levels x 7 stat combinations.
    """
    stat_combos = _all_stat_combos()
    forms: list[str] = []
    for biome_id in biome_ids:
        forms.append(f"{biome_id}_0")
        for level in range(1, 5):
            for combo in stat_combos:
                forms.append(f"{biome_id}_{level}{combo}")
    return forms


def _threshold_level(stat: float) -> int:
    for i, threshold in enumerate(reversed(TRAINING_VISUAL_THRESHOLDS)):
        if stat >= threshold:
            return len(TRAINING_VISUAL_THRESHOLDS) - i
    return 0


def _all_stat_combos() -> list[str]:
    combos: list[tuple[str, ...]] = []
    for r in range(1, 4):
        combos.extend(_combinations(_SORTED_LETTERS, r))
    return ["".join(c) for c in combos]


def _combinations(items: list[str], r: int) -> list[tuple[str, ...]]:
    if r == 0:
        return [()]
    return [
        (items[i], *rest)
        for i in range(len(items))
        for rest in _combinations(items[i + 1 :], r - 1)
    ]
