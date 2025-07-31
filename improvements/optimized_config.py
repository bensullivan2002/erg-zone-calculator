"""
Optimized zone configuration with O(1) lookups.
"""

import json
from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import Dict


class ZoneData(BaseModel):
    """Data model for a single zone configuration."""

    name: str
    lower_bound_coefficient: float
    upper_bound_coefficient: float


class OptimizedZoneConfig:
    """Optimized configuration manager with O(1) zone lookups."""

    def __init__(self, config_file_path: str) -> None:
        self.config_file_path = config_file_path
        self._zones: Dict[str, ZoneData] = {}  # O(1) lookup
        self._zone_order: list[str] = []  # Preserve order
        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration data from file."""
        try:
            with open(Path(self.config_file_path).resolve(), "r") as f:
                raw_data = json.load(f)

            # Validate and store with O(1) access
            for zone_name, zone_data in raw_data.items():
                zone = ZoneData(
                    name=zone_name,
                    lower_bound_coefficient=zone_data["lower_bound"],
                    upper_bound_coefficient=zone_data["upper_bound"],
                )
                self._zones[zone_name] = zone
                self._zone_order.append(zone_name)

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Config file not found at {self.config_file_path}"
            ) from e
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON format in config file at {self.config_file_path}"
            ) from e
        except (ValidationError, KeyError) as e:
            raise ValueError(f"Invalid zone configuration structure: {e}") from e

    def get_zone_names(self) -> list[str]:
        """Get zone names in original order."""
        return self._zone_order.copy()

    def get_zone(self, zone_name: str) -> ZoneData:
        """Get zone data by name - O(1) lookup."""
        if zone_name not in self._zones:
            raise KeyError(f"Zone '{zone_name}' not found in configuration")
        return self._zones[zone_name]

    def get_lower_bound_coefficient(self, zone: str) -> float:
        """Get lower bound coefficient - O(1)."""
        return self.get_zone(zone).lower_bound_coefficient

    def get_upper_bound_coefficient(self, zone: str) -> float:
        """Get upper bound coefficient - O(1)."""
        return self.get_zone(zone).upper_bound_coefficient

    def __contains__(self, zone_name: str) -> bool:
        """Check if zone exists - O(1)."""
        return zone_name in self._zones

    def __len__(self) -> int:
        """Number of zones."""
        return len(self._zones)
