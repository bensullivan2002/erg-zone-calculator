"""
AWS Lambda handler for the ERG Zone Calculator API.
Uses Mangum to adapt FastAPI for Lambda execution.
"""

import logging
import sys
from pathlib import Path

# Add the src directory to the Python path so we can import from it
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mangum import Mangum
from api.app import app

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)

# Create the Lambda handler
handler = Mangum(app, lifespan="off")