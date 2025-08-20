"""
Domain models for Zone and Benchmark objects to eliminate primitive obsession.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .constants import (
    MAX_DISTANCE_METERS,
    MAX_HEART_RATE,
    MAX_TIME_SECONDS,
    MIN_DISTANCE_METERS,
    MIN_HEART_RATE,
    MIN_TIME_SECONDS,
)


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
        if not self._is_valid_coefficient(self.lower_bound_coefficient):
            raise ValueError("Lower bound coefficient must be positive")
        if not self._is_valid_coefficient(self.upper_bound_coefficient):
            raise ValueError("Upper bound coefficient must be positive")

        # Only check ordering if both coefficients are not None
        if not self._has_valid_coefficient_order():
            raise ValueError(
                "Lower bound coefficient must be less than upper bound coefficient"
            )

    def _is_valid_coefficient(self, coefficient: float | None) -> bool:
        """Check if a coefficient is valid (None or positive).

        Args:
            coefficient: The coefficient to validate

        Returns:
            True if coefficient is None or positive, False otherwise
        """
        return coefficient is None or coefficient > 0

    def _has_valid_coefficient_order(self) -> bool:
        """Check if coefficients are in valid order (lower < upper).

        Returns:
            True if coefficients are in valid order or either is None, False otherwise
        """
        if self.lower_bound_coefficient is None or self.upper_bound_coefficient is None:
            return True
        return self.lower_bound_coefficient < self.upper_bound_coefficient


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
        if not (MIN_HEART_RATE <= self.max_hr <= MAX_HEART_RATE):
            raise ValueError(
                f"Maximum heart rate must be between {MIN_HEART_RATE} and {MAX_HEART_RATE} BPM"
            )

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
        if not (MIN_DISTANCE_METERS <= self.distance_meters <= MAX_DISTANCE_METERS):
            raise ValueError(
                f"Distance must be between {MIN_DISTANCE_METERS} and {MAX_DISTANCE_METERS} meters"
            )
        if not (MIN_TIME_SECONDS <= self.time_seconds <= MAX_TIME_SECONDS):
            raise ValueError(
                f"Time must be between {MIN_TIME_SECONDS} and {MAX_TIME_SECONDS} seconds"
            )

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


def create_benchmark(benchmark_type: str, **kwargs) -> Benchmark:
    """Factory method to create benchmark objects.

    Args:
        benchmark_type: Type of benchmark to create ("hr" or "pace")
        **kwargs: Parameters specific to the benchmark type
            - For "hr": max_hr (int)
            - For "pace": distance_meters (int), time_seconds (float)

    Returns:
        Appropriate Benchmark instance

    Raises:
        ValueError: If benchmark_type is invalid or required parameters are missing
    """
    match benchmark_type.lower():
        case "hr":
            if "max_hr" not in kwargs:
                raise ValueError("max_hr parameter required for HR benchmark")
            return HRBenchmark(max_hr=kwargs["max_hr"])
        case "pace":
            if "distance_meters" not in kwargs or "time_seconds" not in kwargs:
                raise ValueError(
                    "distance_meters and time_seconds parameters required for pace benchmark"
                )
            return PaceBenchmark(
                distance_meters=kwargs["distance_meters"],
                time_seconds=kwargs["time_seconds"],
            )
        case _:
            raise ValueError(
                f"Unknown benchmark type: {benchmark_type}. Must be 'hr' or 'pace'"
            )
