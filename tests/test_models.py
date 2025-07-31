"""
Unit tests for Pydantic models.
"""

import pytest
from pydantic import ValidationError

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import (
    HRZoneRequest,
    PaceZoneRequest,
    ZoneResult,
    HRZoneResponse,
    PaceZoneResponse,
    ErrorResponse,
)


class TestHRZoneRequest:
    """Test HRZoneRequest model."""

    def test_valid_request(self):
        """Test valid HR zone request."""
        request = HRZoneRequest(max_hr=185)
        assert request.max_hr == 185
        assert request.config_path == "config/hr_zones.json"  # Default value

    def test_valid_request_with_custom_config(self):
        """Test HR zone request with custom config path."""
        request = HRZoneRequest(max_hr=200, config_path="custom/hr_config.json")
        assert request.max_hr == 200
        assert request.config_path == "custom/hr_config.json"

    def test_max_hr_validation_too_low(self):
        """Test max_hr validation - too low."""
        with pytest.raises(ValidationError) as exc_info:
            HRZoneRequest(max_hr=50)

        errors = exc_info.value.errors()
        assert any("greater than or equal to 100" in str(error) for error in errors)

    def test_max_hr_validation_too_high(self):
        """Test max_hr validation - too high."""
        with pytest.raises(ValidationError) as exc_info:
            HRZoneRequest(max_hr=250)

        errors = exc_info.value.errors()
        assert any("less than or equal to 240" in str(error) for error in errors)

    def test_max_hr_boundary_values(self):
        """Test max_hr boundary values."""
        # Should work
        request_min = HRZoneRequest(max_hr=100)
        request_max = HRZoneRequest(max_hr=240)

        assert request_min.max_hr == 100
        assert request_max.max_hr == 240

    def test_invalid_max_hr_type(self):
        """Test invalid max_hr type."""
        # Pydantic v2 automatically converts string numbers to int
        # Test with a truly invalid type
        with pytest.raises(ValidationError):
            HRZoneRequest(max_hr="not_a_number")  # Invalid string


class TestPaceZoneRequest:
    """Test PaceZoneRequest model."""

    def test_valid_request(self):
        """Test valid pace zone request."""
        request = PaceZoneRequest(distance_meters=2000, time_seconds=420.0)
        assert request.distance_meters == 2000
        assert request.time_seconds == 420.0
        assert request.config_path == "config/pace_zones.json"

    def test_valid_request_with_custom_config(self):
        """Test pace zone request with custom config."""
        request = PaceZoneRequest(
            distance_meters=1000,
            time_seconds=195.5,
            config_path="custom/pace_config.json",
        )
        assert request.distance_meters == 1000
        assert request.time_seconds == 195.5
        assert request.config_path == "custom/pace_config.json"

    def test_distance_validation_too_low(self):
        """Test distance validation - too low."""
        with pytest.raises(ValidationError) as exc_info:
            PaceZoneRequest(distance_meters=400, time_seconds=120.0)

        errors = exc_info.value.errors()
        assert any("greater than or equal to 500" in str(error) for error in errors)

    def test_distance_validation_too_high(self):
        """Test distance validation - too high."""
        with pytest.raises(ValidationError) as exc_info:
            PaceZoneRequest(distance_meters=15000, time_seconds=3000.0)

        errors = exc_info.value.errors()
        assert any("less than or equal to 10000" in str(error) for error in errors)

    def test_time_validation_too_low(self):
        """Test time validation - too low."""
        with pytest.raises(ValidationError) as exc_info:
            PaceZoneRequest(distance_meters=2000, time_seconds=30.0)

        errors = exc_info.value.errors()
        assert any("greater than or equal to 60" in str(error) for error in errors)

    def test_time_validation_too_high(self):
        """Test time validation - too high."""
        with pytest.raises(ValidationError) as exc_info:
            PaceZoneRequest(distance_meters=2000, time_seconds=4000.0)

        errors = exc_info.value.errors()
        assert any("less than or equal to 3600" in str(error) for error in errors)

    def test_boundary_values(self):
        """Test boundary values for distance and time."""
        # Should work
        request = PaceZoneRequest(
            distance_meters=500,  # Min distance
            time_seconds=60.0,  # Min time
        )
        assert request.distance_meters == 500
        assert request.time_seconds == 60.0

        request = PaceZoneRequest(
            distance_meters=10000,  # Max distance
            time_seconds=3600.0,  # Max time
        )
        assert request.distance_meters == 10000
        assert request.time_seconds == 3600.0


class TestZoneResult:
    """Test ZoneResult model."""

    def test_valid_zone_result(self):
        """Test valid zone result."""
        result = ZoneResult(
            zone_name="Zone 1",
            lower_bound=108,
            upper_bound=144,
            lower_bound_formatted="108bpm",
            upper_bound_formatted="144bpm",
            range_formatted="108bpm-144bpm",
        )

        assert result.zone_name == "Zone 1"
        assert result.lower_bound == 108
        assert result.upper_bound == 144
        assert result.lower_bound_formatted == "108bpm"
        assert result.upper_bound_formatted == "144bpm"
        assert result.range_formatted == "108bpm-144bpm"

    def test_zone_result_with_float_bounds(self):
        """Test zone result with float bounds."""
        result = ZoneResult(
            zone_name="UT2",
            lower_bound=123.9,
            upper_bound=130.2,
            lower_bound_formatted="2:03/500m",
            upper_bound_formatted="2:10/500m",
            range_formatted="2:03/500m-2:10/500m",
        )

        assert result.zone_name == "UT2"
        assert result.lower_bound == 123.9
        assert result.upper_bound == 130.2


class TestHRZoneResponse:
    """Test HRZoneResponse model."""

    def test_valid_response(self):
        """Test valid HR zone response."""
        zones = [
            ZoneResult(
                zone_name="Zone 1",
                lower_bound=92,
                upper_bound=111,
                lower_bound_formatted="92bpm",
                upper_bound_formatted="111bpm",
                range_formatted="92bpm-111bpm",
            )
        ]

        response = HRZoneResponse(max_hr=185, zones=zones)
        assert response.max_hr == 185
        assert len(response.zones) == 1
        assert response.zones[0].zone_name == "Zone 1"

    def test_empty_zones_list(self):
        """Test HR response with empty zones list."""
        response = HRZoneResponse(max_hr=185, zones=[])
        assert response.max_hr == 185
        assert len(response.zones) == 0


class TestPaceZoneResponse:
    """Test PaceZoneResponse model."""

    def test_valid_response(self):
        """Test valid pace zone response."""
        zones = [
            ZoneResult(
                zone_name="UT2",
                lower_bound=123.9,
                upper_bound=130.2,
                lower_bound_formatted="2:03/500m",
                upper_bound_formatted="2:10/500m",
                range_formatted="2:03/500m-2:10/500m",
            )
        ]

        response = PaceZoneResponse(
            distance_meters=2000,
            time_seconds=420.0,
            benchmark_pace="1:45/500m",
            zones=zones,
        )

        assert response.distance_meters == 2000
        assert response.time_seconds == 420.0
        assert response.benchmark_pace == "1:45/500m"
        assert len(response.zones) == 1


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response_with_detail(self):
        """Test error response with detail."""
        error = ErrorResponse(
            error="Configuration file not found",
            detail="Config file not found at config/hr_zones.json",
        )

        assert error.error == "Configuration file not found"
        assert error.detail == "Config file not found at config/hr_zones.json"

    def test_error_response_without_detail(self):
        """Test error response without detail."""
        error = ErrorResponse(error="Invalid input")

        assert error.error == "Invalid input"
        assert error.detail is None

    def test_error_response_serialization(self):
        """Test error response serialization."""
        error = ErrorResponse(error="Test error", detail="Test detail")

        data = error.model_dump()
        assert data["error"] == "Test error"
        assert data["detail"] == "Test detail"
