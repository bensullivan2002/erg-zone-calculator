import json
from src.calculate_pace_zones import PaceZoneCalculator
import pytest


class TestPaceZoneCalculatorShould:
    @pytest.mark.parametrize(
        "two_km_time, precision, expected_exception",
        [
            (-1, 1, ValueError),
            (1, -1, ValueError),
            ("invalid", 1, TypeError),  # type: ignore
            (400, "invalid", TypeError),  # type: ignore
        ],
    )
    def test_reject_invalid_arguments_for_PaceZoneCalculator_constructor(self, two_km_time, precision, expected_exception):
        with pytest.raises(expected_exception):
            PaceZoneCalculator(two_km_time, precision)

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

    def test_reject_invalid_arguments_for_calculate_lower_bound_time_per_500m(self):
        calculator = PaceZoneCalculator(400, 1)
        with pytest.raises(TypeError):
            calculator.calculate_lower_bound_time_per_500m(123, "config/pace_zones.json") # type: ignore
        with pytest.raises(TypeError):
            calculator.calculate_lower_bound_time_per_500m("UT2", 123) # type: ignore
        with pytest.raises(FileNotFoundError):
            calculator.calculate_lower_bound_time_per_500m("UT2", "invalid_path.json")
        with pytest.raises(json.JSONDecodeError):
            calculator.calculate_lower_bound_time_per_500m("UT3", "test/fixtures/invalid_pace_zones.json")
        with pytest.raises(KeyError):
            calculator.calculate_lower_bound_time_per_500m("INVALID_ZONE", "config/pace_zones.json")
    
    @pytest.mark.parametrize(
        "two_km_time,zone,expected_upper_bound, precision",
        [
            (415, "UT2", 128.1, 1),
            (400, "UT1", 116.28, 2),
            (450, "AT", 123.626, 3),
            (415, "TR", 108.1, 1),
            (415, "AC", 103.7, 1),
            (415, "AP", 103.7, 1),
        ],
    )
    def test_calculate_upper_bound_time_per_500m(
        self, two_km_time, zone, expected_upper_bound, precision
    ):
        config_file_path = "config/pace_zones.json"
        calculator = PaceZoneCalculator(two_km_time, precision)
        upper_bound = calculator.calculate_upper_bound_time_per_500m(
            zone, config_file_path
        )
        assert upper_bound == expected_upper_bound

    def test_reject_invalid_arguments_for_calculate_upper_bound_time_per_500m(self):
        calculator = PaceZoneCalculator(400, 1)
        with pytest.raises(TypeError):
            calculator.calculate_upper_bound_time_per_500m(123, "config/pace_zones.json") # type: ignore
        with pytest.raises(TypeError):
            calculator.calculate_upper_bound_time_per_500m("UT2", 123) # type: ignore
        with pytest.raises(FileNotFoundError):
            calculator.calculate_upper_bound_time_per_500m("UT2", "invalid_path.json")
        with pytest.raises(json.JSONDecodeError):
            calculator.calculate_upper_bound_time_per_500m("UT3", "test/fixtures/invalid_pace_zones.json")
        with pytest.raises(KeyError):
            calculator.calculate_upper_bound_time_per_500m("INVALID_ZONE", "config/pace_zones.json")
