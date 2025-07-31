"""
Domain-specific exceptions for better error handling.
"""

import json
from pathlib import Path
from zone_configs import ZoneData


class ZoneCalculatorError(Exception):
    """Base exception for zone calculator errors."""

    pass


class ConfigurationError(ZoneCalculatorError):
    """Raised when there's an issue with zone configuration."""

    def __init__(self, message: str, config_path: str | None = None):
        self.config_path = config_path
        super().__init__(message)


class ZoneNotFoundError(ZoneCalculatorError):
    """Raised when a requested zone doesn't exist."""

    def __init__(self, zone_name: str, available_zones: list[str] | None = None):
        self.zone_name = zone_name
        self.available_zones = available_zones or []

        message = f"Zone '{zone_name}' not found"
        if self.available_zones:
            message += f". Available zones: {', '.join(self.available_zones)}"

        super().__init__(message)


class InvalidBenchmarkError(ZoneCalculatorError):
    """Raised when benchmark values are invalid."""

    def __init__(self, message: str, benchmark_value: any = None):
        self.benchmark_value = benchmark_value
        super().__init__(message)


class CalculationError(ZoneCalculatorError):
    """Raised when zone calculation fails."""

    def __init__(self, message: str, zone: str | None = None):
        self.zone = zone
        super().__init__(message)


# Usage in improved zone config:
class ImprovedZoneConfig:
    """Zone config with specific exceptions."""

    def get_zone(self, zone_name: str) -> ZoneData:
        """Get zone with specific exception."""
        if zone_name not in self._zones:
            raise ZoneNotFoundError(zone_name, list(self._zones.keys()))
        return self._zones[zone_name]

    def _load_config(self) -> None:
        """Load config with specific exceptions."""
        try:
            with open(Path(self.config_file_path).resolve(), "r") as f:
                json.load(f)  # Load but don't store unused variable
        except FileNotFoundError as e:
            raise ConfigurationError(
                f"Config file not found at {self.config_file_path}",
                self.config_file_path,
            ) from e
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in config file: {e}", self.config_file_path
            ) from e

        # Validation logic with specific errors...


# Usage in calculators:
# Note: HRBenchmark would be imported from type_safe_calculators.py
class ImprovedHRZoneCalculator:
    """HR calculator with specific exceptions."""

    def calculate_lower_bound(self, zone: str, benchmark: int) -> int:
        try:
            coefficient = self.zone_config.get_lower_bound_coefficient(zone)
            result = benchmark * coefficient

            if result <= 0:
                raise CalculationError(f"Invalid calculation result: {result}", zone)

            return int(result)

        except ZoneNotFoundError:
            raise  # Re-raise specific exceptions
        except Exception as e:
            raise CalculationError(
                f"Unexpected error calculating zone {zone}: {e}", zone
            ) from e
