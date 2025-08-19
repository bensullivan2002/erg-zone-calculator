"""
Tests for domain models (Zone and Benchmark classes).
"""

import pytest
from src.domain.domain_models import (
    Zone,
    HRBenchmark,
    PaceBenchmark,
    create_benchmark_from_primitives,
)


class TestZone:
    """Test Zone domain model."""

    def test_valid_zone_creation(self):
        """Test creating a valid zone."""
        zone = Zone(
            name="UT2",
            lower_bound_coefficient=0.60,
            upper_bound_coefficient=0.67,
        )
        assert zone.name == "UT2"
        assert zone.lower_bound_coefficient == 0.60
        assert zone.upper_bound_coefficient == 0.67

    def test_zone_with_none_coefficients(self):
        """Test creating a zone with None coefficients for open-ended zones."""
        # Lower bound None (e.g., UT3)
        zone1 = Zone(
            name="UT3",
            lower_bound_coefficient=None,
            upper_bound_coefficient=0.59,
        )
        assert zone1.lower_bound_coefficient is None
        assert zone1.upper_bound_coefficient == 0.59

        # Upper bound None (e.g., AC/AP)
        zone2 = Zone(
            name="AC",
            lower_bound_coefficient=1.0,
            upper_bound_coefficient=None,
        )
        assert zone2.lower_bound_coefficient == 1.0
        assert zone2.upper_bound_coefficient is None

    def test_zone_validation_empty_name(self):
        """Test zone validation with empty name."""
        with pytest.raises(ValueError, match="Zone name cannot be empty"):
            Zone(
                name="",
                lower_bound_coefficient=0.60,
                upper_bound_coefficient=0.67,
            )

    def test_zone_validation_negative_coefficients(self):
        """Test zone validation with negative coefficients."""
        with pytest.raises(ValueError, match="Lower bound coefficient must be positive"):
            Zone(
                name="Test",
                lower_bound_coefficient=-0.1,
                upper_bound_coefficient=0.67,
            )

        with pytest.raises(ValueError, match="Upper bound coefficient must be positive"):
            Zone(
                name="Test",
                lower_bound_coefficient=0.60,
                upper_bound_coefficient=-0.1,
            )

    def test_zone_validation_coefficient_ordering(self):
        """Test zone validation with incorrect coefficient ordering."""
        with pytest.raises(ValueError, match="Lower bound coefficient must be less than upper bound coefficient"):
            Zone(
                name="Test",
                lower_bound_coefficient=0.80,
                upper_bound_coefficient=0.60,
            )


class TestHRBenchmark:
    """Test HRBenchmark domain model."""

    def test_valid_hr_benchmark_creation(self):
        """Test creating a valid HR benchmark."""
        benchmark = HRBenchmark(max_hr=185)
        assert benchmark.max_hr == 185

    def test_hr_benchmark_validation_too_low(self):
        """Test HR benchmark validation with too low value."""
        with pytest.raises(ValueError, match="Maximum heart rate must be between 100 and 240 BPM"):
            HRBenchmark(max_hr=90)

    def test_hr_benchmark_validation_too_high(self):
        """Test HR benchmark validation with too high value."""
        with pytest.raises(ValueError, match="Maximum heart rate must be between 100 and 240 BPM"):
            HRBenchmark(max_hr=250)

    def test_hr_benchmark_calculate_zone_bounds(self):
        """Test HR benchmark zone bounds calculation."""
        benchmark = HRBenchmark(max_hr=180)
        zone = Zone(
            name="UT2",
            lower_bound_coefficient=0.60,
            upper_bound_coefficient=0.67,
        )

        lower, upper = benchmark.calculate_zone_bounds(zone)
        assert lower == 108  # 180 * 0.60
        assert upper == 120  # 180 * 0.67 (rounded down)

    def test_hr_benchmark_calculate_zone_bounds_with_none(self):
        """Test HR benchmark zone bounds calculation with None coefficients."""
        benchmark = HRBenchmark(max_hr=180)
        
        # Zone with None lower bound
        zone1 = Zone(
            name="UT3",
            lower_bound_coefficient=None,
            upper_bound_coefficient=0.59,
        )
        lower, upper = benchmark.calculate_zone_bounds(zone1)
        assert lower is None
        assert upper == 106  # 180 * 0.59

        # Zone with None upper bound
        zone2 = Zone(
            name="AC",
            lower_bound_coefficient=1.0,
            upper_bound_coefficient=None,
        )
        lower, upper = benchmark.calculate_zone_bounds(zone2)
        assert lower == 180  # 180 * 1.0
        assert upper is None


class TestPaceBenchmark:
    """Test PaceBenchmark domain model."""

    def test_valid_pace_benchmark_creation(self):
        """Test creating a valid pace benchmark."""
        benchmark = PaceBenchmark(distance_meters=2000, time_seconds=420.0)
        assert benchmark.distance_meters == 2000
        assert benchmark.time_seconds == 420.0

    def test_pace_benchmark_validation_distance_too_low(self):
        """Test pace benchmark validation with distance too low."""
        with pytest.raises(ValueError, match="Distance must be between 500 and 10000 meters"):
            PaceBenchmark(distance_meters=400, time_seconds=120.0)

    def test_pace_benchmark_validation_distance_too_high(self):
        """Test pace benchmark validation with distance too high."""
        with pytest.raises(ValueError, match="Distance must be between 500 and 10000 meters"):
            PaceBenchmark(distance_meters=15000, time_seconds=1800.0)

    def test_pace_benchmark_validation_time_too_low(self):
        """Test pace benchmark validation with time too low."""
        with pytest.raises(ValueError, match="Time must be between 60 and 3600 seconds"):
            PaceBenchmark(distance_meters=2000, time_seconds=30.0)

    def test_pace_benchmark_validation_time_too_high(self):
        """Test pace benchmark validation with time too high."""
        with pytest.raises(ValueError, match="Time must be between 60 and 3600 seconds"):
            PaceBenchmark(distance_meters=2000, time_seconds=4000.0)

    def test_pace_benchmark_base_500m_time(self):
        """Test pace benchmark base 500m time calculation."""
        benchmark = PaceBenchmark(distance_meters=2000, time_seconds=420.0)
        assert benchmark.base_500m_time == 105.0  # 420 / (2000/500) = 420/4 = 105

        benchmark2 = PaceBenchmark(distance_meters=1000, time_seconds=195.0)
        assert benchmark2.base_500m_time == 97.5  # 195 / (1000/500) = 195/2 = 97.5

    def test_pace_benchmark_calculate_zone_bounds(self):
        """Test pace benchmark zone bounds calculation."""
        benchmark = PaceBenchmark(distance_meters=2000, time_seconds=420.0)  # 105s per 500m
        zone = Zone(
            name="UT2",
            lower_bound_coefficient=0.81,
            upper_bound_coefficient=0.85,
        )

        lower, upper = benchmark.calculate_zone_bounds(zone)
        assert lower == pytest.approx(85.05)  # 105 * 0.81
        assert upper == pytest.approx(89.25)  # 105 * 0.85

    def test_pace_benchmark_calculate_zone_bounds_with_none(self):
        """Test pace benchmark zone bounds calculation with None coefficients."""
        benchmark = PaceBenchmark(distance_meters=2000, time_seconds=420.0)  # 105s per 500m
        
        # Zone with None lower bound
        zone1 = Zone(
            name="UT3",
            lower_bound_coefficient=None,
            upper_bound_coefficient=0.8,
        )
        lower, upper = benchmark.calculate_zone_bounds(zone1)
        assert lower is None
        assert upper == pytest.approx(84.0)  # 105 * 0.8

        # Zone with None upper bound
        zone2 = Zone(
            name="AC",
            lower_bound_coefficient=1.0,
            upper_bound_coefficient=None,
        )
        lower, upper = benchmark.calculate_zone_bounds(zone2)
        assert lower == pytest.approx(105.0)  # 105 * 1.0
        assert upper is None


class TestBenchmarkFactory:
    """Test benchmark factory function."""

    def test_create_hr_benchmark_from_int(self):
        """Test creating HR benchmark from int."""
        benchmark = create_benchmark_from_primitives(185)
        assert isinstance(benchmark, HRBenchmark)
        assert benchmark.max_hr == 185

    def test_create_hr_benchmark_from_float(self):
        """Test creating HR benchmark from float."""
        benchmark = create_benchmark_from_primitives(185.0)
        assert isinstance(benchmark, HRBenchmark)
        assert benchmark.max_hr == 185

    def test_create_pace_benchmark_from_tuple(self):
        """Test creating pace benchmark from tuple."""
        benchmark = create_benchmark_from_primitives((2000, 420.0))
        assert isinstance(benchmark, PaceBenchmark)
        assert benchmark.distance_meters == 2000
        assert benchmark.time_seconds == 420.0

    def test_create_benchmark_invalid_input(self):
        """Test creating benchmark with invalid input."""
        with pytest.raises(ValueError, match="benchmark_value must be either maxHR"):
            create_benchmark_from_primitives("invalid")

        with pytest.raises(ValueError, match="benchmark_value must be either maxHR"):
            create_benchmark_from_primitives((1000,))  # Tuple with wrong length

        with pytest.raises(ValueError, match="benchmark_value must be either maxHR"):
            create_benchmark_from_primitives([2000, 420.0])  # List instead of tuple