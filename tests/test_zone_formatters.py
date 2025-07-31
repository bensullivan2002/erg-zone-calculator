"""
Unit tests for ZoneFormatter classes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from zone_formatters import HRFormatter, PaceFormatter, VerbosePaceFormatter


class TestHRFormatter:
    """Test HRFormatter class."""

    def test_format_value_integer(self):
        """Test formatting integer HR values."""
        formatter = HRFormatter()

        assert formatter.format_value(120) == "120bpm"
        assert formatter.format_value(85) == "85bpm"
        assert formatter.format_value(200) == "200bpm"

    def test_format_value_float(self):
        """Test formatting float HR values (should convert to int)."""
        formatter = HRFormatter()

        assert formatter.format_value(120.7) == "120bpm"
        assert formatter.format_value(85.2) == "85bpm"
        assert formatter.format_value(199.9) == "199bpm"

    def test_format_zone_bounds(self):
        """Test formatting HR zone bounds."""
        formatter = HRFormatter()

        result = formatter.format_zone_bounds(108, 144)
        assert result == "108bpm-144bpm"

        result = formatter.format_zone_bounds(92.5, 111.3)
        assert result == "92bpm-111bpm"


class TestPaceFormatter:
    """Test PaceFormatter class."""

    def test_format_value_basic(self):
        """Test basic pace formatting."""
        formatter = PaceFormatter()

        # Test exact minutes
        assert formatter.format_value(120) == "2:00/500m"
        assert formatter.format_value(60) == "1:00/500m"
        assert formatter.format_value(180) == "3:00/500m"

    def test_format_value_with_seconds(self):
        """Test pace formatting with seconds."""
        formatter = PaceFormatter()

        assert formatter.format_value(105) == "1:45/500m"
        assert formatter.format_value(95) == "1:35/500m"
        assert formatter.format_value(125) == "2:05/500m"

    def test_format_value_under_minute(self):
        """Test pace formatting under one minute."""
        formatter = PaceFormatter()

        assert formatter.format_value(45) == "0:45/500m"
        assert formatter.format_value(30) == "0:30/500m"
        assert formatter.format_value(5) == "0:05/500m"

    def test_format_value_float(self):
        """Test pace formatting with float values."""
        formatter = PaceFormatter()

        assert formatter.format_value(105.7) == "1:45/500m"  # Truncated to int
        assert formatter.format_value(119.2) == "1:59/500m"

    def test_format_zone_bounds(self):
        """Test formatting pace zone bounds."""
        formatter = PaceFormatter()

        result = formatter.format_zone_bounds(105, 120)
        assert result == "1:45/500m-2:00/500m"

        result = formatter.format_zone_bounds(95.5, 110.8)
        assert result == "1:35/500m-1:50/500m"

    def test_format_value_long_times(self):
        """Test pace formatting with longer times."""
        formatter = PaceFormatter()

        assert formatter.format_value(300) == "5:00/500m"  # 5 minutes
        assert formatter.format_value(245) == "4:05/500m"  # 4:05
        assert formatter.format_value(3661) == "61:01/500m"  # Over an hour


class TestVerbosePaceFormatter:
    """Test VerbosePaceFormatter class."""

    def test_format_value_minutes_and_seconds(self):
        """Test verbose formatting with minutes and seconds."""
        formatter = VerbosePaceFormatter()

        assert formatter.format_value(105) == "1 min 45 sec/500m"
        assert formatter.format_value(125) == "2 min 5 sec/500m"
        assert formatter.format_value(95) == "1 min 35 sec/500m"

    def test_format_value_exact_minutes(self):
        """Test verbose formatting with exact minutes."""
        formatter = VerbosePaceFormatter()

        assert formatter.format_value(60) == "1 min/500m"
        assert formatter.format_value(120) == "2 min/500m"
        assert formatter.format_value(180) == "3 min/500m"

    def test_format_value_seconds_only(self):
        """Test verbose formatting with seconds only."""
        formatter = VerbosePaceFormatter()

        assert formatter.format_value(45) == "45 sec/500m"
        assert formatter.format_value(30) == "30 sec/500m"
        assert formatter.format_value(5) == "5 sec/500m"

    def test_format_value_float(self):
        """Test verbose formatting with float values."""
        formatter = VerbosePaceFormatter()

        assert formatter.format_value(105.7) == "1 min 45 sec/500m"
        assert formatter.format_value(119.2) == "1 min 59 sec/500m"

    def test_format_zone_bounds(self):
        """Test verbose formatting of zone bounds."""
        formatter = VerbosePaceFormatter()

        result = formatter.format_zone_bounds(105, 120)
        assert result == "1 min 45 sec/500m-2 min/500m"

        result = formatter.format_zone_bounds(45, 95)
        assert result == "45 sec/500m-1 min 35 sec/500m"

    def test_format_value_long_times(self):
        """Test verbose formatting with longer times."""
        formatter = VerbosePaceFormatter()

        assert formatter.format_value(300) == "5 min/500m"
        assert formatter.format_value(245) == "4 min 5 sec/500m"


class TestFormatterConsistency:
    """Test consistency between different formatters."""

    def test_all_formatters_handle_same_input(self):
        """Test that all formatters can handle the same input values."""
        hr_formatter = HRFormatter()
        pace_formatter = PaceFormatter()
        verbose_formatter = VerbosePaceFormatter()

        # Test with various values
        test_values = [60, 105, 120, 180, 45.5, 119.9]

        for value in test_values:
            # All should return strings
            hr_result = hr_formatter.format_value(value)
            pace_result = pace_formatter.format_value(value)
            verbose_result = verbose_formatter.format_value(value)

            assert isinstance(hr_result, str)
            assert isinstance(pace_result, str)
            assert isinstance(verbose_result, str)

            # HR should end with 'bpm'
            assert hr_result.endswith("bpm")

            # Pace formatters should end with '/500m'
            assert pace_result.endswith("/500m")
            assert verbose_result.endswith("/500m")

    def test_zone_bounds_formatting_consistency(self):
        """Test that zone bounds formatting is consistent."""
        formatters = [HRFormatter(), PaceFormatter(), VerbosePaceFormatter()]

        for formatter in formatters:
            result = formatter.format_zone_bounds(100, 120)

            # Should contain a dash
            assert "-" in result

            # Should have two parts when split by dash
            parts = result.split("-")
            assert len(parts) == 2

            # Both parts should be valid formatted values
            lower_part = parts[0]
            upper_part = parts[1]

            assert lower_part == formatter.format_value(100)
            assert upper_part == formatter.format_value(120)
