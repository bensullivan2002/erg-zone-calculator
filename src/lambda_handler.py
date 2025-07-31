"""
AWS Lambda handler for the ERG Zone Calculator API.
Uses Mangum to adapt FastAPI for Lambda execution.
"""

from mangum import Mangum
from app import app

# Create the Lambda handler
handler = Mangum(app, lifespan="off")

# For debugging in Lambda
import logging
logging.basicConfig(level=logging.INFO)