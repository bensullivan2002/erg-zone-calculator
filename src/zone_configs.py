import json
from pathlib import Path
from pydantic import BaseModel, ValidationError


class ZoneData(BaseModel):
    """Data model for a single zone configuration."""

    name: str
    lower_bound_coefficient: float
    upper_bound_coefficient: float


class ZoneConfig:
    """Configuration manager for training zones."""

    def __init__(self, config_file_path: str) -> None:
        """Initialize with a configuration file path.

        Args:
            config_file_path: Path to the JSON configuration file
        """
        self.config_file_path = config_file_path
        self._zones: list[ZoneData] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load and validate configuration data from file."""
        try:
            with open(Path(self.config_file_path).resolve(), "r") as f:
                raw_data = json.load(f)

            # Validate each zone using Pydantic
            for zone_name, zone_data in raw_data.items():
                self._zones.append(
                    ZoneData(
                        name=zone_name,
                        lower_bound_coefficient=zone_data["lower_bound"],
                        upper_bound_coefficient=zone_data["upper_bound"],
                    )
                )

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
        """Get all available zone names from the configuration.

        Returns:
            List of zone names
        """
        return [zone.name for zone in self._zones]

    def _get_zone(self, zone_name: str) -> ZoneData:
        """Get zone data by name.

        Args:
            zone_name: The zone name to find

        Returns:
            The ZoneData object

        Raises:
            KeyError: If the zone doesn't exist in the configuration
        """
        for zone in self._zones:
            if zone.name == zone_name:
                return zone
        raise KeyError(f"Zone '{zone_name}' not found in configuration")

    def get_lower_bound_coefficient(self, zone: str) -> float:
        """Get the lower bound coefficient for a zone.

        Args:
            zone: The zone name

        Returns:
            The coefficient used to calculate the lower bound

        Raises:
            KeyError: If the zone doesn't exist in the configuration
        """
        return self._get_zone(zone).lower_bound_coefficient

    def get_upper_bound_coefficient(self, zone: str) -> float:
        """Get the upper bound coefficient for a zone.

        Args:
            zone: The zone name

        Returns:
            The coefficient used to calculate the upper bound

        Raises:
            KeyError: If the zone doesn't exist in the configuration
        """
        return self._get_zone(zone).upper_bound_coefficient
