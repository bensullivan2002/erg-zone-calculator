"""
Pytest configuration and shared fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path for all tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def sample_hr_config_data():
    """Sample HR configuration data for testing."""
    return {
        "Zone 1": {"lower_bound": 0.5, "upper_bound": 0.6},
        "Zone 2": {"lower_bound": 0.6, "upper_bound": 0.7},
        "Zone 3": {"lower_bound": 0.7, "upper_bound": 0.8},
        "Zone 4": {"lower_bound": 0.8, "upper_bound": 0.9},
        "Zone 5": {"lower_bound": 0.9, "upper_bound": 1.0}
    }


@pytest.fixture(scope="session")
def sample_pace_config_data():
    """Sample pace configuration data for testing."""
    return {
        "UT2": {"lower_bound": 1.18, "upper_bound": 1.24},
        "UT1": {"lower_bound": 1.08, "upper_bound": 1.15},
        "AT": {"lower_bound": 1.02, "upper_bound": 1.06},
        "TR": {"lower_bound": 0.97, "upper_bound": 1.02},
        "AN": {"lower_bound": 0.93, "upper_bound": 0.97}
    }