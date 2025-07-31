"""
AWS Lambda handler for the ERG Zone Calculator API.
Uses Mangum to adapt FastAPI for Lambda execution.
"""

import logging
from mangum import Mangum
from app import app

# Configure logging for Lambda
logging.basicConfig(level=logging.INFO)

# Create the Lambda handler
handler = Mangum(app, lifespan="off")
