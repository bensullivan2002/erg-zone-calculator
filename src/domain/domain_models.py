"""
Domain models for Zone and Benchmark objects to eliminate primitive obsession.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Zone:
    """Represents a training zone with its name and coefficients."""

    name: str
    lower_bound_coefficient: float | None
    upper_bound_coefficient: float | None

    def __post_init__(self):
        """Validate zone data after initialization."""
        if not self.name.strip():
            raise ValueError("Zone name cannot be empty")

        # Allow None values for open-ended zones
        if (
            self.lower_bound_coefficient is not None
            and self.lower_bound_coefficient <= 0
        ):
            raise ValueError("Lower bound coefficient must be positive")
        if (
            self.upper_bound_coefficient is not None
            and self.upper_bound_coefficient <= 0
        ):
            raise ValueError("Upper bound coefficient must be positive")

        # Only check ordering if both coefficients are not None
        if (
            self.lower_bound_coefficient is not None
            and self.upper_bound_coefficient is not None
            and self.lower_bound_coefficient >= self.upper_bound_coefficient
        ):
            raise ValueError(
                "Lower bound coefficient must be less than upper bound coefficient"
            )


class Benchmark(ABC):
    """Abstract base class for performance benchmarks."""

    @abstractmethod
    def calculate_zone_bounds(self, zone: Zone) -> tuple[int | float, int | float]:
        """Calculate the lower and upper bounds for a given zone.

        Args:
            zone: The zone to calculate bounds for

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        pass


@dataclass(frozen=True)
class HRBenchmark(Benchmark):
    """Heart rate benchmark for calculating HR zones."""

    max_hr: int

    def __post_init__(self):
        """Validate HR benchmark data."""
        if not (100 <= self.max_hr <= 240):
            raise ValueError("Maximum heart rate must be between 100 and 240 BPM")

    def calculate_zone_bounds(self, zone: Zone) -> tuple[int | None, int | None]:
        """Calculate HR zone bounds.

        Args:
            zone: The zone to calculate bounds for

        Returns:
            Tuple of (lower_bound_hr, upper_bound_hr) as integers or None for open-ended zones
        """
        lower_bound = (
            None
            if zone.lower_bound_coefficient is None
            else int(self.max_hr * zone.lower_bound_coefficient)
        )
        upper_bound = (
            None
            if zone.upper_bound_coefficient is None
            else int(self.max_hr * zone.upper_bound_coefficient)
        )
        return lower_bound, upper_bound


@dataclass(frozen=True)
class PaceBenchmark(Benchmark):
    """Pace benchmark for calculating pace zones."""

    distance_meters: int
    time_seconds: float

    def __post_init__(self):
        """Validate pace benchmark data."""
        if not (500 <= self.distance_meters <= 10000):
            raise ValueError("Distance must be between 500 and 10000 meters")
        if not (60 <= self.time_seconds <= 3600):
            raise ValueError("Time must be between 60 and 3600 seconds")

    @property
    def base_500m_time(self) -> float:
        """Calculate the base 500m time from the benchmark performance.

        Returns:
            Time per 500m in seconds
        """
        return self.time_seconds / (self.distance_meters / 500)

    def calculate_zone_bounds(self, zone: Zone) -> tuple[float | None, float | None]:
        """Calculate pace zone bounds.

        Args:
            zone: The zone to calculate bounds for

        Returns:
            Tuple of (lower_bound_time, upper_bound_time) as floats (seconds per 500m) or None for open-ended zones
        """
        base_time = self.base_500m_time
        lower_bound = (
            None
            if zone.lower_bound_coefficient is None
            else base_time * zone.lower_bound_coefficient
        )
        upper_bound = (
            None
            if zone.upper_bound_coefficient is None
            else base_time * zone.upper_bound_coefficient
        )
        return lower_bound, upper_bound


def create_benchmark_from_primitives(
    benchmark_value: int | float | tuple[int, float],
) -> Benchmark:
    """Factory function to create benchmark objects from primitive values.

    Args:
        benchmark_value: Either maxHR (int) or (distance_meters, time_seconds) tuple

    Returns:
        Appropriate Benchmark instance

    Raises:
        ValueError: If benchmark_value format is invalid
    """
    if isinstance(benchmark_value, (int, float)) and not isinstance(
        benchmark_value, tuple
    ):
        return HRBenchmark(max_hr=int(benchmark_value))
    elif isinstance(benchmark_value, tuple) and len(benchmark_value) == 2:
        distance_meters, time_seconds = benchmark_value
        return PaceBenchmark(
            distance_meters=int(distance_meters), time_seconds=float(time_seconds)
        )
    else:
        raise ValueError(
            "benchmark_value must be either maxHR (int) or (distance_meters, time_seconds) tuple"
        )