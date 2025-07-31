from abc import ABC, abstractmethod
from zone_configs import ZoneConfig


class ZoneCalculator(ABC):
    """Abstract base class for zone calculators."""

    def __init__(self, zone_config: ZoneConfig) -> None:
        """Initialize with a zone configuration.

        Args:
            zone_config: Configuration object containing zone definitions
        """
        self.zone_config = zone_config

    @abstractmethod
    def calculate_lower_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> int | float:
        """Calculate the lower bound for a given zone.

        Args:
            zone: The zone name to calculate bounds for (e.g., "UT2 or Zone 2")
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            The lower bound numeric value (int for HR, float for pace)
        """
        pass

    @abstractmethod
    def calculate_upper_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> int | float:
        """Calculate the upper bound for a given zone.

        Args:
            zone: The zone name to calculate bounds for (e.g., "UT2 or Zone 2")
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            The upper bound numeric value (int for HR, float for pace)
        """
        pass

    def calculate_all_lower_bounds(
        self, benchmark_value: int | float | tuple[int, float]
    ) -> dict[str, int | float]:
        """Calculate lower bounds for all zones in the configuration.

        Args:
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Dictionary mapping zone names to their lower bound numeric values
        """
        return {
            zone: self.calculate_lower_bound(zone, benchmark_value)
            for zone in self.zone_config.get_zone_names()
        }

    def calculate_all_upper_bounds(
        self, benchmark_value: int | float | tuple[int, float]
    ) -> dict[str, int | float]:
        """Calculate upper bounds for all zones in the configuration.

        Args:
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Dictionary mapping zone names to their upper bound numeric values
        """
        return {
            zone: self.calculate_upper_bound(zone, benchmark_value)
            for zone in self.zone_config.get_zone_names()
        }


class HRZoneCalculator(ZoneCalculator):
    """Heart rate zone calculator."""

    def __init__(self, zone_config: ZoneConfig) -> None:
        """Initialize HR zone calculator.

        Args:
            zone_config: Configuration containing HR zone definitions
        """
        super().__init__(zone_config)

    def calculate_lower_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> int:
        """Calculate the lower bound heart rate for a given zone.

        Args:
            zone: The zone name to calculate bounds for
            benchmark_value: Maximum heart rate (maxHR) as int

        Returns:
            Lower bound heart rate as integer (e.g., 108)
        """
        if isinstance(benchmark_value, tuple):
            raise ValueError("HR calculator expects maxHR as int, not tuple")

        coefficient = self.zone_config.get_lower_bound_coefficient(zone)
        lower_bound_hr = benchmark_value * coefficient
        return int(lower_bound_hr)

    def calculate_upper_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> int:
        """Calculate the upper bound heart rate for a given zone.

        Args:
            zone: The zone name to calculate bounds for
            benchmark_value: Maximum heart rate (maxHR) as int

        Returns:
            Upper bound heart rate as integer (e.g., 144)
        """
        if isinstance(benchmark_value, tuple):
            raise ValueError("HR calculator expects maxHR as int, not tuple")

        coefficient = self.zone_config.get_upper_bound_coefficient(zone)
        upper_bound_hr = benchmark_value * coefficient
        return int(upper_bound_hr)


class PaceZoneCalculator(ZoneCalculator):
    """Pace zone calculator for rowing/ergometer training."""

    def __init__(self, zone_config: ZoneConfig) -> None:
        """Initialize pace zone calculator.

        Args:
            zone_config: Configuration containing pace zone definitions
        """
        super().__init__(zone_config)

    def calculate_lower_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> float:
        """Calculate the lower bound pace for a given zone.

        Args:
            zone: The zone name to calculate bounds for
            benchmark_value: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Lower bound time per 500m in seconds (e.g., 105.5)
        """
        if not isinstance(benchmark_value, tuple):
            raise ValueError(
                "Pace calculator expects (distance_meters, time_seconds) tuple"
            )

        distance_meters, time_seconds = benchmark_value
        coefficient = self.zone_config.get_lower_bound_coefficient(zone)

        # Convert any distance/time to 500m base time, then apply coefficient
        base_500m_time = time_seconds / (distance_meters / 500)
        lower_bound_time = base_500m_time * coefficient
        return lower_bound_time

    def calculate_upper_bound(
        self, zone: str, benchmark_value: int | float | tuple[int, float]
    ) -> float:
        """Calculate the upper bound pace for a given zone.

        Args:
            zone: The zone name to calculate bounds for
            benchmark_value: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Upper bound time per 500m in seconds (e.g., 120.0)
        """
        if not isinstance(benchmark_value, tuple):
            raise ValueError(
                "Pace calculator expects (distance_meters, time_seconds) tuple"
            )

        distance_meters, time_seconds = benchmark_value
        coefficient = self.zone_config.get_upper_bound_coefficient(zone)

        # Convert any distance/time to 500m base time, then apply coefficient
        base_500m_time = time_seconds / (distance_meters / 500)
        upper_bound_time = base_500m_time * coefficient
        return upper_bound_time
