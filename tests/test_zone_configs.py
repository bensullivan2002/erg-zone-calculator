"""
Unit tests for ZoneConfig class.
"""

import pytest
import json
import tempfile
from pathlib import Path
from pydantic import ValidationError

import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from zone_configs import ZoneConfig, ZoneData


class TestZoneData:
    """Test ZoneData Pydantic model."""

    def test_valid_zone_data(self):
        """Test creating valid ZoneData."""
        zone = ZoneData(
            name="Zone 1", lower_bound_coefficient=0.5, upper_bound_coefficient=0.6
        )
        assert zone.name == "Zone 1"
        assert zone.lower_bound_coefficient == 0.5
        assert zone.upper_bound_coefficient == 0.6

    def test_zone_data_validation(self):
        """Test ZoneData validation."""
        # Missing required fields
        with pytest.raises(ValidationError):
            ZoneData(name="Zone 1")

        # Invalid types
        with pytest.raises(ValidationError):
            ZoneData(
                name=123,  # Should be string
                lower_bound_coefficient=0.5,
                upper_bound_coefficient=0.6,
            )


class TestZoneConfig:
    """Test ZoneConfig class."""

    def create_temp_config(self, config_data):
        """Helper to create temporary config file."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        return temp_file.name

    def test_valid_config_loading(self):
        """Test loading valid configuration."""
        config_data = {
            "Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6},
            "Zone 2": {"lower_bound": 0.6, "upper_bound": 0.7},
        }
        config_path = self.create_temp_config(config_data)

        try:
            config = ZoneConfig(config_path)
            assert len(config._zones) == 2
            assert config.get_zone_names() == ["Zone 1", "Zone 2"]
        finally:
            Path(config_path).unlink()

    def test_file_not_found(self):
        """Test handling of missing config file."""
        with pytest.raises(FileNotFoundError, match="Config file not found"):
            ZoneConfig("nonexistent.json")

    def test_invalid_json(self):
        """Test handling of invalid JSON."""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
        temp_file.write("invalid json content")
        temp_file.close()

        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                ZoneConfig(temp_file.name)
        finally:
            Path(temp_file.name).unlink()

    def test_invalid_zone_structure(self):
        """Test handling of invalid zone structure."""
        config_data = {
            "Zone 1": {"lower_bound": 0.5},  # Missing upper_bound
            "Zone 2": {"lower_bound": 0.6, "upper_bound": 0.7},
        }
        config_path = self.create_temp_config(config_data)

        try:
            with pytest.raises(
                ValueError, match="Invalid zone configuration structure"
            ):
                ZoneConfig(config_path)
        finally:
            Path(config_path).unlink()

    def test_get_zone_names(self):
        """Test getting zone names."""
        config_data = {
            "UT2": {"lower_bound": 1.18, "upper_bound": 1.24},
            "UT1": {"lower_bound": 1.08, "upper_bound": 1.15},
            "AT": {"lower_bound": 1.02, "upper_bound": 1.06},
        }
        config_path = self.create_temp_config(config_data)

        try:
            config = ZoneConfig(config_path)
            zone_names = config.get_zone_names()
            assert zone_names == ["UT2", "UT1", "AT"]
        finally:
            Path(config_path).unlink()

    def test_get_coefficients(self):
        """Test getting zone coefficients."""
        config_data = {"Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6}}
        config_path = self.create_temp_config(config_data)

        try:
            config = ZoneConfig(config_path)
            assert config.get_lower_bound_coefficient("Zone 1") == 0.5
            assert config.get_upper_bound_coefficient("Zone 1") == 0.6
        finally:
            Path(config_path).unlink()

    def test_invalid_zone_name(self):
        """Test handling of invalid zone names."""
        config_data = {"Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6}}
        config_path = self.create_temp_config(config_data)

        try:
            config = ZoneConfig(config_path)
            with pytest.raises(KeyError, match="Zone 'Invalid' not found"):
                config.get_lower_bound_coefficient("Invalid")
        finally:
            Path(config_path).unlink()

    def test_relative_path_resolution(self):
        """Test that relative paths are resolved correctly."""
        config_data = {"Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6}}

        # Create temp file in current directory
        temp_path = Path("temp_config.json")
        with open(temp_path, "w") as f:
            json.dump(config_data, f)

        try:
            # Use relative path
            config = ZoneConfig("temp_config.json")
            assert len(config._zones) == 1
        finally:
            temp_path.unlink()
