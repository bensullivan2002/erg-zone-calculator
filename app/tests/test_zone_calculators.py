"""
Unit tests for ZoneCalculator classes.
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from domain.zone_configs import ZoneConfig
from domain.zone_calculators import HRZoneCalculator, PaceZoneCalculator


class TestHRZoneCalculator:
    """Test HRZoneCalculator class."""

    @pytest.fixture
    def hr_config(self):
        """Create HR zone configuration for testing."""
        config_data = {
            "Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6},
            "Zone 2": {"lower_bound": 0.6, "upper_bound": 0.7},
            "Zone 3": {"lower_bound": 0.7, "upper_bound": 0.8},
        }
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()

        config = ZoneConfig(temp_file.name)
        yield config

        Path(temp_file.name).unlink()

    def test_calculate_lower_bound(self, hr_config):
        """Test HR lower bound calculation."""
        calculator = HRZoneCalculator(hr_config)

        # Test with maxHR = 180
        result = calculator.calculate_lower_bound("Zone 1", 180)
        assert result == 90  # 180 * 0.5 = 90
        assert isinstance(result, int)

        result = calculator.calculate_lower_bound("Zone 2", 180)
        assert result == 108  # 180 * 0.6 = 108

    def test_calculate_upper_bound(self, hr_config):
        """Test HR upper bound calculation."""
        calculator = HRZoneCalculator(hr_config)

        result = calculator.calculate_upper_bound("Zone 1", 180)
        assert result == 108  # 180 * 0.6 = 108
        assert isinstance(result, int)

    def test_calculate_all_bounds(self, hr_config):
        """Test calculating all HR zone bounds."""
        calculator = HRZoneCalculator(hr_config)

        all_lower = calculator.calculate_all_lower_bounds(180)
        all_upper = calculator.calculate_all_upper_bounds(180)

        assert len(all_lower) == 3
        assert len(all_upper) == 3
        assert all_lower["Zone 1"] == 90
        assert all_upper["Zone 1"] == 108

    def test_invalid_benchmark_type(self, hr_config):
        """Test HR calculator with invalid benchmark type."""
        calculator = HRZoneCalculator(hr_config)

        with pytest.raises(ValueError, match="HR calculator expects maxHR as int"):
            calculator.calculate_lower_bound("Zone 1", (2000, 420.0))

    def test_invalid_zone_name(self, hr_config):
        """Test HR calculator with invalid zone name."""
        calculator = HRZoneCalculator(hr_config)

        with pytest.raises(KeyError, match="Zone 'Invalid' not found"):
            calculator.calculate_lower_bound("Invalid", 180)

    def test_fractional_hr_rounding(self, hr_config):
        """Test that fractional HR values are rounded to integers."""
        calculator = HRZoneCalculator(hr_config)

        # Use maxHR that creates fractional results
        result = calculator.calculate_lower_bound("Zone 1", 185)
        assert result == 92  # int(185 * 0.5) = int(92.5) = 92
        assert isinstance(result, int)


class TestPaceZoneCalculator:
    """Test PaceZoneCalculator class."""

    @pytest.fixture
    def pace_config(self):
        """Create pace zone configuration for testing."""
        config_data = {
            "UT2": {"lower_bound": 1.18, "upper_bound": 1.24},
            "UT1": {"lower_bound": 1.08, "upper_bound": 1.15},
            "AT": {"lower_bound": 1.02, "upper_bound": 1.06},
        }
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()

        config = ZoneConfig(temp_file.name)
        yield config

        Path(temp_file.name).unlink()

    def test_calculate_lower_bound(self, pace_config):
        """Test pace lower bound calculation."""
        calculator = PaceZoneCalculator(pace_config)

        # 2000m in 420 seconds = 105 seconds per 500m base
        benchmark = (2000, 420.0)
        result = calculator.calculate_lower_bound("UT2", benchmark)

        # Base 500m time: 420 / (2000/500) = 420 / 4 = 105
        # UT2 lower: 105 * 1.18 = 123.9
        expected = 105.0 * 1.18
        assert abs(result - expected) < 0.01
        assert isinstance(result, float)

    def test_calculate_upper_bound(self, pace_config):
        """Test pace upper bound calculation."""
        calculator = PaceZoneCalculator(pace_config)

        benchmark = (2000, 420.0)
        result = calculator.calculate_upper_bound("UT2", benchmark)

        expected = 105.0 * 1.24
        assert abs(result - expected) < 0.01

    def test_different_distances(self, pace_config):
        """Test pace calculation with different distances."""
        calculator = PaceZoneCalculator(pace_config)

        # Test with 1000m
        benchmark_1k = (1000, 195.0)  # 1000m in 195s = 97.5s per 500m
        result_1k = calculator.calculate_lower_bound("UT2", benchmark_1k)
        expected_1k = 97.5 * 1.18
        assert abs(result_1k - expected_1k) < 0.01

        # Test with 5000m
        benchmark_5k = (5000, 1200.0)  # 5000m in 1200s = 120s per 500m
        result_5k = calculator.calculate_lower_bound("UT2", benchmark_5k)
        expected_5k = 120.0 * 1.18
        assert abs(result_5k - expected_5k) < 0.01

    def test_calculate_all_bounds(self, pace_config):
        """Test calculating all pace zone bounds."""
        calculator = PaceZoneCalculator(pace_config)

        benchmark = (2000, 420.0)
        all_lower = calculator.calculate_all_lower_bounds(benchmark)
        all_upper = calculator.calculate_all_upper_bounds(benchmark)

        assert len(all_lower) == 3
        assert len(all_upper) == 3
        assert "UT2" in all_lower
        assert "UT1" in all_lower
        assert "AT" in all_lower

    def test_invalid_benchmark_type(self, pace_config):
        """Test pace calculator with invalid benchmark type."""
        calculator = PaceZoneCalculator(pace_config)

        with pytest.raises(ValueError, match="Pace calculator expects.*tuple"):
            calculator.calculate_lower_bound("UT2", 180)

    def test_invalid_zone_name(self, pace_config):
        """Test pace calculator with invalid zone name."""
        calculator = PaceZoneCalculator(pace_config)

        with pytest.raises(KeyError, match="Zone 'Invalid' not found"):
            calculator.calculate_lower_bound("Invalid", (2000, 420.0))

    def test_edge_case_distances(self, pace_config):
        """Test pace calculation with edge case distances."""
        calculator = PaceZoneCalculator(pace_config)

        # Test with 500m (should be 1:1 ratio)
        benchmark_500 = (500, 105.0)
        result = calculator.calculate_lower_bound("UT2", benchmark_500)
        expected = 105.0 * 1.18  # Direct multiplication since it's already 500m
        assert abs(result - expected) < 0.01
