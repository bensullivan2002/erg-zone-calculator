"""
Property-based tests using Hypothesis.
"""

from hypothesis import given, strategies as st, assume
import pytest
import tempfile
import json
from pathlib import Path

# Import the improved classes
from type_safe_calculators import HRZoneCalculator, PaceZoneCalculator, HRBenchmark, PaceBenchmark
from optimized_config import OptimizedZoneConfig
from domain_models import ZoneBounds, TrainingZone


class TestZoneCalculatorProperties:
    """Property-based tests for zone calculators."""

    @given(
        max_hr=st.integers(min_value=100, max_value=240),
        coefficient=st.floats(min_value=0.1, max_value=1.0),
    )
    def test_hr_calculation_properties(self, max_hr, coefficient):
        """Test HR calculation properties hold for all valid inputs."""
        result = max_hr * coefficient

        # Properties that should always hold:
        assert result >= 0, "HR calculation should never be negative"
        assert result <= max_hr, "Calculated HR should not exceed max HR"
        assert int(result) == int(max_hr * coefficient), (
            "Integer conversion should be consistent"
        )

    @given(
        distance=st.integers(min_value=500, max_value=10000),
        time=st.floats(min_value=60.0, max_value=3600.0),
        coefficient=st.floats(min_value=0.8, max_value=1.5),
    )
    def test_pace_calculation_properties(self, distance, time, coefficient):
        """Test pace calculation properties."""
        assume(time > 0 and distance > 0)  # Ensure valid inputs

        base_500m_time = time / (distance / 500)
        result = base_500m_time * coefficient

        # Properties:
        assert result > 0, "Pace should always be positive"
        assert result < 3600, "Pace should be reasonable (< 1 hour per 500m)"

        # Scaling property: doubling distance should halve base pace
        double_distance_base = time / ((distance * 2) / 500)
        assert abs(double_distance_base - base_500m_time / 2) < 0.001

    @given(
        values=st.lists(
            st.floats(min_value=0.1, max_value=2.0), min_size=2, max_size=10
        )
    )
    def test_zone_ordering_properties(self, values):
        """Test that zone bounds maintain proper ordering."""
        # Sort to ensure proper ordering
        sorted_values = sorted(values)

        # Create mock zones
        zones = []
        for i in range(len(sorted_values) - 1):
            lower = sorted_values[i]
            upper = sorted_values[i + 1]

            # Properties:
            assert lower < upper, "Lower bound must be less than upper"

            # No overlapping zones
            if zones:
                prev_upper = zones[-1][1]
                assert lower >= prev_upper, "Zones should not overlap"

            zones.append((lower, upper))

    @given(
        zone_count=st.integers(min_value=1, max_value=10),
        base_value=st.floats(min_value=50.0, max_value=300.0),
    )
    def test_zone_coverage_properties(self, zone_count, base_value):
        """Test that zones provide reasonable coverage."""
        # Generate coefficients that increase
        coefficients = sorted([0.5 + (i * 0.1) for i in range(zone_count * 2)])

        zones = []
        for i in range(zone_count):
            lower_coeff = coefficients[i * 2]
            upper_coeff = coefficients[i * 2 + 1]

            lower = base_value * lower_coeff
            upper = base_value * upper_coeff

            zones.append((lower, upper))

        # Properties:
        # 1. Each zone should have reasonable width
        for lower, upper in zones:
            width = upper - lower
            assert width > 0, "Zone must have positive width"
            assert width < base_value, "Zone width should be reasonable"

        # 2. Zones should cover a reasonable range
        total_range = zones[-1][1] - zones[0][0]
        assert total_range > base_value * 0.2, "Total range should be significant"


# Add to requirements.txt: hypothesis>=6.0.0
# Run with: pytest improvements/property_tests.py

class TestImprovedZoneCalculators:
    """Property-based tests for the improved calculators."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary config file for testing."""
        config_data = {
            "Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6},
            "Zone 2": {"lower_bound": 0.6, "upper_bound": 0.7},
            "Zone 3": {"lower_bound": 0.7, "upper_bound": 0.8}
        }
        
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(config_data, temp_file)
        temp_file.close()
        
        yield temp_file.name
        Path(temp_file.name).unlink()
    
    @given(max_hr=st.integers(min_value=100, max_value=240))
    def test_hr_benchmark_validation(self, max_hr):
        """Test HR benchmark validation properties."""
        benchmark = HRBenchmark(max_hr=max_hr)
        
        # Properties that should always hold
        assert 100 <= benchmark.max_hr <= 240
        assert isinstance(benchmark.max_hr, int)
    
    @given(
        max_hr=st.integers(min_value=50, max_value=99) | 
               st.integers(min_value=241, max_value=300)
    )
    def test_hr_benchmark_invalid_values(self, max_hr):
        """Test that invalid HR values are rejected."""
        with pytest.raises(ValueError):
            HRBenchmark(max_hr=max_hr)
    
    @given(
        distance=st.integers(min_value=500, max_value=10000),
        time=st.floats(min_value=60.0, max_value=3600.0)
    )
    def test_pace_benchmark_properties(self, distance, time):
        """Test pace benchmark properties."""
        assume(time > 0 and distance > 0)
        
        benchmark = PaceBenchmark(distance_meters=distance, time_seconds=time)
        
        # Properties
        assert benchmark.distance_meters > 0
        assert benchmark.time_seconds > 0
        assert benchmark.base_500m_time > 0
        
        # Mathematical property: base_500m_time should scale correctly
        expected_base = time / (distance / 500)
        assert abs(benchmark.base_500m_time - expected_base) < 0.001
    
    @given(
        lower=st.floats(min_value=50.0, max_value=150.0),
        upper=st.floats(min_value=151.0, max_value=250.0)
    )
    def test_zone_bounds_properties(self, lower, upper):
        """Test zone bounds value object properties."""
        bounds = ZoneBounds(lower=lower, upper=upper)
        
        # Properties
        assert bounds.lower < bounds.upper
        assert bounds.range_size == upper - lower
        assert bounds.midpoint == (lower + upper) / 2
        
        # Containment properties
        assert bounds.contains(bounds.midpoint)
        assert bounds.contains(lower)
        assert bounds.contains(upper)
        assert not bounds.contains(lower - 1)
        assert not bounds.contains(upper + 1)
    
    @given(
        zone_name=st.text(min_size=1, max_size=20),
        lower=st.floats(min_value=50.0, max_value=150.0),
        upper=st.floats(min_value=151.0, max_value=250.0)
    )
    def test_training_zone_properties(self, zone_name, lower, upper):
        """Test training zone domain model properties."""
        assume(zone_name.strip())  # Non-empty after stripping
        
        bounds = ZoneBounds(lower=lower, upper=upper)
        zone = TrainingZone(name=zone_name.strip(), bounds=bounds)
        
        # Properties
        assert zone.name == zone_name.strip()
        assert zone.bounds == bounds
        assert zone.intensity_level in ["Low", "Moderate", "High", "Very High", "Unknown"]
        
        # Behavior properties
        assert zone.is_target_zone(bounds.midpoint)
        assert zone.distance_from_zone(bounds.midpoint) == 0.0
        
        # Distance calculation properties
        outside_value = upper + 10
        distance = zone.distance_from_zone(outside_value)
        assert distance > 0
        assert distance == outside_value - upper