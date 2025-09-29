"""
Infrastructure constants for deployment and configuration.
"""

from pathlib import Path

# Application paths
APP_ROOT = Path(__file__).parent.parent.parent
STATIC_DIR = APP_ROOT / "app" / "src" / "static"
STATIC_INDEX_FILE = STATIC_DIR / "index.html"

# API construct
ROOT_DOMAIN_NAME = "zonecalculator.com"
API_NAME = "erg-zone-calculator-api"
ALLOW_ORIGINS = [f"https://{ROOT_DOMAIN_NAME}"]
ALLOW_HEADERS = ["Content-Type", "Authorization"]

# Lambda runtime
PYTHONPATH = "/var/task/app/src"