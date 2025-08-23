"""
Domain constants for validation and business rules.
"""
from pathlib import Path

# Heart Rate validation bounds
MIN_HEART_RATE = 100
MAX_HEART_RATE = 240

# Pace validation bounds
MIN_DISTANCE_METERS = 500
MAX_DISTANCE_METERS = 10000
MIN_TIME_SECONDS = 60
MAX_TIME_SECONDS = 3600

# Application paths
APP_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = APP_ROOT / "static"
STATIC_INDEX_FILE = STATIC_DIR / "index.html"
