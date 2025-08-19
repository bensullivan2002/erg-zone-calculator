from abc import ABC, abstractmethod
from .zone_configs import ZoneConfig
from .domain_models import Zone, create_benchmark_from_primitives


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

    def calculate_zone_bounds(
        self, zone_name: str, benchmark_value: int | float | tuple[int, float]
    ) -> tuple[int | float | None, int | float | None]:
        """Calculate both bounds for a zone using domain objects.

        Args:
            zone_name: The zone name to calculate bounds for
            benchmark_value: The performance benchmark value

        Returns:
            Tuple of (lower_bound, upper_bound), where bounds can be None for open-ended zones
        """
        # Create domain objects from primitives
        zone = Zone(
            name=zone_name,
            lower_bound_coefficient=self.zone_config.get_lower_bound_coefficient(zone_name),
            upper_bound_coefficient=self.zone_config.get_upper_bound_coefficient(zone_name),
        )
        benchmark = create_benchmark_from_primitives(benchmark_value)
        
        # Use domain object methods
        return benchmark.calculate_zone_bounds(zone)

    def calculate_all_lower_bounds(
        self, benchmark_value: int | float | tuple[int, float]
    ) -> dict[str, int | float | None]:
        """Calculate lower bounds for all zones in the configuration.

        Args:
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Dictionary mapping zone names to their lower bound numeric values (or None for open-ended zones)
        """
        result = {}
        for zone_name in self.zone_config.get_zone_names():
            try:
                result[zone_name] = self.calculate_lower_bound(zone_name, benchmark_value)
            except ValueError:
                # Zone has no lower bound (open-ended)
                result[zone_name] = None
        return result

    def calculate_all_upper_bounds(
        self, benchmark_value: int | float | tuple[int, float]
    ) -> dict[str, int | float | None]:
        """Calculate upper bounds for all zones in the configuration.

        Args:
            benchmark_value: The performance benchmark value:
                - For HR: maxHR as int (e.g., 180)
                - For pace: (distance_meters, time_seconds) tuple (e.g., (2000, 420.0))

        Returns:
            Dictionary mapping zone names to their upper bound numeric values (or None for open-ended zones)
        """
        result = {}
        for zone_name in self.zone_config.get_zone_names():
            try:
                result[zone_name] = self.calculate_upper_bound(zone_name, benchmark_value)
            except ValueError:
                # Zone has no upper bound (open-ended)
                result[zone_name] = None
        return result


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

        # Use domain objects for calculation
        lower_bound, _ = self.calculate_zone_bounds(zone, benchmark_value)
        if lower_bound is None:
            raise ValueError(f"Zone '{zone}' has no lower bound defined")
        return lower_bound

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

        # Use domain objects for calculation
        _, upper_bound = self.calculate_zone_bounds(zone, benchmark_value)
        if upper_bound is None:
            raise ValueError(f"Zone '{zone}' has no upper bound defined")
        return upper_bound


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

        # Use domain objects for calculation
        lower_bound, _ = self.calculate_zone_bounds(zone, benchmark_value)
        if lower_bound is None:
            raise ValueError(f"Zone '{zone}' has no lower bound defined")
        return lower_bound

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

        # Use domain objects for calculation
        _, upper_bound = self.calculate_zone_bounds(zone, benchmark_value)
        if upper_bound is None:
            raise ValueError(f"Zone '{zone}' has no upper bound defined")
        return upper_bound