"""
Rich domain models with business logic.
"""

from dataclasses import dataclass
from typing import Protocol
from abc import abstractmethod


class ZoneFormatter(Protocol):
    """Protocol for zone formatters."""

    @abstractmethod
    def format_value(self, value: int | float) -> str: ...


@dataclass(frozen=True)
class ZoneBounds:
    """Value object representing zone boundaries."""

    lower: int | float
    upper: int | float

    def __post_init__(self):
        if self.lower >= self.upper:
            raise ValueError(
                f"Lower bound ({self.lower}) must be less than upper bound ({self.upper})"
            )

    @property
    def range_size(self) -> float:
        """Calculate the size of the zone range."""
        return float(self.upper - self.lower)

    @property
    def midpoint(self) -> float:
        """Calculate the midpoint of the zone."""
        return (self.lower + self.upper) / 2

    def contains(self, value: int | float) -> bool:
        """Check if a value falls within this zone."""
        return self.lower <= value <= self.upper

    def format_with(self, formatter: ZoneFormatter) -> str:
        """Format the bounds using the provided formatter."""
        return (
            f"{formatter.format_value(self.lower)}-{formatter.format_value(self.upper)}"
        )


@dataclass(frozen=True)
class TrainingZone:
    """Rich domain model for a training zone."""

    name: str
    bounds: ZoneBounds
    description: str = ""

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Zone name cannot be empty")

    @property
    def intensity_level(self) -> str:
        """Determine intensity level based on zone name patterns."""
        name_lower = self.name.lower()
        if any(x in name_lower for x in ["recovery", "zone 1", "ut2"]):
            return "Low"
        elif any(x in name_lower for x in ["aerobic", "zone 2", "zone 3", "ut1"]):
            return "Moderate"
        elif any(x in name_lower for x in ["threshold", "zone 4", "at"]):
            return "High"
        elif any(x in name_lower for x in ["vo2max", "zone 5", "an", "tr"]):
            return "Very High"
        else:
            return "Unknown"

    def is_target_zone(self, value: int | float) -> bool:
        """Check if a value is in this zone."""
        return self.bounds.contains(value)

    def distance_from_zone(self, value: int | float) -> float:
        """Calculate distance from zone (0 if inside, positive if outside)."""
        if self.bounds.contains(value):
            return 0.0
        elif value < self.bounds.lower:
            return float(self.bounds.lower - value)
        else:
            return float(value - self.bounds.upper)


@dataclass
class ZoneCalculationResult:
    """Result of zone calculations with rich domain logic."""

    zones: list[TrainingZone]
    benchmark_description: str

    def get_zone_by_name(self, name: str) -> TrainingZone | None:
        """Find zone by name."""
        return next((z for z in self.zones if z.name == name), None)

    def find_target_zone(self, value: int | float) -> TrainingZone | None:
        """Find which zone a value falls into."""
        return next((z for z in self.zones if z.is_target_zone(value)), None)

    def get_zones_by_intensity(self, intensity: str) -> list[TrainingZone]:
        """Get all zones of a specific intensity level."""
        return [z for z in self.zones if z.intensity_level == intensity]

    @property
    def zone_count(self) -> int:
        """Number of zones."""
        return len(self.zones)

    @property
    def total_range(self) -> tuple[float, float]:
        """Overall range across all zones."""
        if not self.zones:
            return (0.0, 0.0)

        min_lower = min(z.bounds.lower for z in self.zones)
        max_upper = max(z.bounds.upper for z in self.zones)
        return (float(min_lower), float(max_upper))
