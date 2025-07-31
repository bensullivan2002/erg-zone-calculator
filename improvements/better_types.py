"""
Type-safe zone calculators using protocols and generics.
"""

from abc import ABC, abstractmethod
from typing import Protocol, TypeVar, Generic
from dataclasses import dataclass
from zone_configs import ZoneConfig


# Define proper types for benchmark values
@dataclass(frozen=True)
class HRBenchmark:
    """Heart rate benchmark value."""

    max_hr: int

    def __post_init__(self):
        if not 100 <= self.max_hr <= 240:
            raise ValueError(f"Invalid max HR: {self.max_hr}")


@dataclass(frozen=True)
class PaceBenchmark:
    """Pace benchmark value."""

    distance_meters: int
    time_seconds: float

    def __post_init__(self):
        if self.distance_meters <= 0 or self.time_seconds <= 0:
            raise ValueError("Distance and time must be positive")

    @property
    def base_500m_time(self) -> float:
        """Calculate base 500m time."""
        return self.time_seconds / (self.distance_meters / 500)


# Protocol for benchmark values
class Benchmark(Protocol):
    """Protocol for benchmark values."""

    pass


# Generic calculator
T = TypeVar("T", bound=Benchmark)
R = TypeVar("R", int, float)


class ZoneCalculator(ABC, Generic[T, R]):
    """Type-safe zone calculator."""

    def __init__(self, zone_config: ZoneConfig) -> None:
        self.zone_config = zone_config

    @abstractmethod
    def calculate_lower_bound(self, zone: str, benchmark: T) -> R:
        pass

    @abstractmethod
    def calculate_upper_bound(self, zone: str, benchmark: T) -> R:
        pass


class HRZoneCalculator(ZoneCalculator[HRBenchmark, int]):
    """Type-safe HR calculator."""

    def calculate_lower_bound(self, zone: str, benchmark: HRBenchmark) -> int:
        coefficient = self.zone_config.get_lower_bound_coefficient(zone)
        return int(benchmark.max_hr * coefficient)

    def calculate_upper_bound(self, zone: str, benchmark: HRBenchmark) -> int:
        coefficient = self.zone_config.get_upper_bound_coefficient(zone)
        return int(benchmark.max_hr * coefficient)


class PaceZoneCalculator(ZoneCalculator[PaceBenchmark, float]):
    """Type-safe pace calculator."""

    def calculate_lower_bound(self, zone: str, benchmark: PaceBenchmark) -> float:
        coefficient = self.zone_config.get_lower_bound_coefficient(zone)
        return benchmark.base_500m_time * coefficient

    def calculate_upper_bound(self, zone: str, benchmark: PaceBenchmark) -> float:
        coefficient = self.zone_config.get_upper_bound_coefficient(zone)
        return benchmark.base_500m_time * coefficient
