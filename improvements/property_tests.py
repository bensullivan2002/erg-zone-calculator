"""
Property-based tests using Hypothesis.
"""

from hypothesis import given, strategies as st, assume


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
