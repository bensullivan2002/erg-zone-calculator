"""
AWS Lambda handler for the ERG Zone Calculator API.
Uses Mangum to adapt FastAPI for Lambda execution.
"""

import logging
import sys
from pathlib import Path

from mangum import Mangum

# Add the src directory to the Python path so we can import from it
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from api.app import app  # noqa: E402

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)

# Create the Lambda handler
handler = Mangum(app, lifespan="off")
