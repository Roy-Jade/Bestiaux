import pytest

from bestiaux.compendium.domain import (
    _threshold_level,
    all_possible_form_ids,
    compute_form_id,
)


class TestThresholdLevel:
    def test_zero_for_stat_below_first_threshold(self) -> None:
        assert _threshold_level(0.0) == 0
        assert _threshold_level(24.9) == 0

    def test_level_1_at_25(self) -> None:
        assert _threshold_level(25.0) == 1
        assert _threshold_level(49.9) == 1

    def test_level_2_at_50(self) -> None:
        assert _threshold_level(50.0) == 2
        assert _threshold_level(74.9) == 2

    def test_level_3_at_75(self) -> None:
        assert _threshold_level(75.0) == 3
        assert _threshold_level(99.9) == 3

    def test_level_4_at_100(self) -> None:
        assert _threshold_level(100.0) == 4


class TestComputeFormId:
    def test_base_form_when_no_threshold_reached(self) -> None:
        assert compute_form_id("mountain", 0.0, 0.0, 0.0) == "mountain_0"
        assert compute_form_id("mountain", 24.9, 20.0, 10.0) == "mountain_0"

    def test_single_dominant_stat(self) -> None:
        # force=77 (T3), beauty=35 (T1), size=65 (T2) → max=3 → 3S
        assert compute_form_id("mountain", 77.0, 35.0, 65.0) == "mountain_3S"

    def test_two_dominant_stats(self) -> None:
        # force=58 (T2), beauty=67 (T2), size=44 (T1) → max=2 → 2BS
        assert compute_form_id("mountain", 58.0, 67.0, 44.0) == "mountain_2BS"

    def test_all_three_dominant_stats(self) -> None:
        # all at threshold 1 → 1BSW
        assert compute_form_id("ocean", 25.0, 25.0, 25.0) == "ocean_1BSW"

    def test_letters_sorted_alphabetically(self) -> None:
        # force(S) and size(W) at T2, beauty(B) at T1 → 2SW
        assert compute_form_id("forest", 60.0, 30.0, 60.0) == "forest_2SW"

    def test_biome_id_in_prefix(self) -> None:
        result = compute_form_id("marine", 100.0, 100.0, 100.0)
        assert result.startswith("marine_")

    def test_perfect_form(self) -> None:
        assert compute_form_id("mountain", 100.0, 100.0, 100.0) == "mountain_4BSW"

    @pytest.mark.parametrize("biome_id", ["mountain", "marine", "forest"])
    def test_biome_prefix_preserved(self, biome_id: str) -> None:
        form_id = compute_form_id(biome_id, 50.0, 0.0, 0.0)
        assert form_id == f"{biome_id}_2S"


class TestAllPossibleFormIds:
    def test_produces_29_forms_per_biome(self) -> None:
        forms = all_possible_form_ids(["mountain"])
        assert len(forms) == 29

    def test_includes_base_form(self) -> None:
        forms = all_possible_form_ids(["mountain"])
        assert "mountain_0" in forms

    def test_includes_all_levels(self) -> None:
        forms = all_possible_form_ids(["mountain"])
        for level in range(1, 5):
            assert any(f"mountain_{level}" in f for f in forms)

    def test_includes_all_stat_combos_per_level(self) -> None:
        forms = all_possible_form_ids(["ocean"])
        expected_combos = ["B", "S", "W", "BS", "BW", "SW", "BSW"]
        for combo in expected_combos:
            assert f"ocean_1{combo}" in forms

    def test_scales_with_multiple_biomes(self) -> None:
        forms = all_possible_form_ids(["mountain", "marine", "forest"])
        assert len(forms) == 87  # 29 * 3

    def test_each_biome_has_its_own_forms(self) -> None:
        forms = all_possible_form_ids(["mountain", "marine"])
        mountain_forms = [f for f in forms if f.startswith("mountain_")]
        marine_forms = [f for f in forms if f.startswith("marine_")]
        assert len(mountain_forms) == 29
        assert len(marine_forms) == 29
