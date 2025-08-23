"""
FastAPI application for ERG Zone Calculator.
Provides REST API endpoints for calculating training zones.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from pathlib import Path
from datetime import datetime


from .models import (
    HRZoneRequest,
    PaceZoneRequest,
    HRZoneResponse,
    PaceZoneResponse,
    ZoneResult,
    ErrorResponse,
)
from src.domain.zone_configs import ZoneConfig
from src.domain.zone_calculators import HRZoneCalculator, PaceZoneCalculator
from src.domain.zone_formatters import HRFormatter, PaceFormatter
from src.domain.constants import STATIC_DIR, STATIC_INDEX_FILE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ERG Zone Calculator API",
    description="Calculate training zones for heart rate and pace in rowing/ergometer workouts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Serve the main landing page."""
    return FileResponse(STATIC_INDEX_FILE)


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "message": "ERG Zone Calculator API",
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "service": "erg-zone-calculator",
        "timestamp": datetime.utcnow(),
    }


@app.post("/calculate/hr-zones", response_model=HRZoneResponse)
async def calculate_hr_zones(request: HRZoneRequest):
    """
    Calculate heart rate training zones.

    Takes a maximum heart rate and returns calculated zone boundaries
    with both numeric values and formatted strings.
    """
    try:
        logger.info(f"Calculating HR zones for maxHR: {request.max_hr}")

        # Load configuration and create calculator
        config = ZoneConfig(request.config_path)
        calculator = HRZoneCalculator(config)
        formatter = HRFormatter()

        # Calculate all zones
        all_lower = calculator.calculate_all_lower_bounds(request.max_hr)
        all_upper = calculator.calculate_all_upper_bounds(request.max_hr)

        # Format results
        zones = []
        for zone_name in config.get_zone_names():
            lower = all_lower[zone_name]
            upper = all_upper[zone_name]

            zone_result = ZoneResult(
                zone_name=zone_name,
                lower_bound=lower,
                upper_bound=upper,
                lower_bound_formatted=formatter.format_value(lower),
                upper_bound_formatted=formatter.format_value(upper),
                range_formatted=formatter.format_zone_bounds(lower, upper),
            )
            zones.append(zone_result)

        return HRZoneResponse(max_hr=request.max_hr, zones=zones)

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file not found: {request.config_path}",
        )
    except ValueError as e:
        logger.error(f"Invalid configuration: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calculating HR zones: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error calculating HR zones"
        )


@app.post("/calculate/pace-zones", response_model=PaceZoneResponse)
async def calculate_pace_zones(request: PaceZoneRequest):
    """
    Calculate pace training zones.

    Takes a distance and time performance and returns calculated zone boundaries
    with both numeric values and formatted strings.
    """
    try:
        logger.info(
            f"Calculating pace zones for {request.distance_meters}m in {request.time_seconds}s"
        )

        # Load configuration and create calculator
        config = ZoneConfig(request.config_path)
        calculator = PaceZoneCalculator(config)
        formatter = PaceFormatter()

        # Prepare benchmark tuple
        benchmark = (request.distance_meters, request.time_seconds)

        # Calculate benchmark pace for display
        base_500m_time = request.time_seconds / (request.distance_meters / 500)
        benchmark_pace = formatter.format_value(base_500m_time)

        # Calculate all zones
        all_lower = calculator.calculate_all_lower_bounds(benchmark)
        all_upper = calculator.calculate_all_upper_bounds(benchmark)

        # Format results
        zones = []
        for zone_name in config.get_zone_names():
            lower = all_lower[zone_name]
            upper = all_upper[zone_name]

            zone_result = ZoneResult(
                zone_name=zone_name,
                lower_bound=lower,
                upper_bound=upper,
                lower_bound_formatted=formatter.format_value(lower),
                upper_bound_formatted=formatter.format_value(upper),
                range_formatted=formatter.format_zone_bounds(lower, upper),
            )
            zones.append(zone_result)

        return PaceZoneResponse(
            distance_meters=request.distance_meters,
            time_seconds=request.time_seconds,
            benchmark_pace=benchmark_pace,
            zones=zones,
        )

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Configuration file not found: {request.config_path}",
        )
    except ValueError as e:
        logger.error(f"Invalid configuration or input: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error calculating pace zones: {e}")
        raise HTTPException(
            status_code=500, detail="Internal server error calculating pace zones"
        )


# Exception handler for custom error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail, detail=None).model_dump(),
    )


if __name__ == "__main__":
    # For local development only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
