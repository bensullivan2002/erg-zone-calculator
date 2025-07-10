from src.calculate_pace_zones import PaceZoneCalculator
import pytest


class TestPaceZoneCalculatorShould:
    @pytest.mark.parametrize(
        "two_km_time,zone,expected_lower_bound, precision",
        [
            (415, "UT2", 128.1, 1),
            (400, "UT1", 116.28, 2),
            (450, "AT", 123.626, 3),
            (415, "TR", 108.1, 1),
            (415, "AC", 103.7, 1),
            (415, "AP", 103.7, 1),
        ],
    )
    def test_calculate_lower_bound_time_per_500m(
        self, two_km_time, zone, expected_lower_bound, precision
    ):
        config_file_path = "config/pace_zones.json"
        calculator = PaceZoneCalculator(two_km_time, precision)
        lower_bound = calculator.calculate_lower_bound_time_per_500m(
            zone, config_file_path
        )
        assert lower_bound == expected_lower_bound

    def test_reject_calculation_for_negative_times(self):
        with pytest.raises(ValueError):
            PaceZoneCalculator(-1, 1)

    def test_reject_calculation_for_invalid_two_km_time_format(self):
        with pytest.raises(TypeError):
            PaceZoneCalculator("invalid", 1)
