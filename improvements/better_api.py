"""
Improved API design with versioning and standards.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
import logging

# Import your existing models and classes
from models import HRZoneRequest
from zone_configs import ZoneConfig
from zone_calculators import HRZoneCalculator
from zone_formatters import HRFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API Response Standards
class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool
    data: dict | list | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class PaginatedResponse(APIResponse):
    """Paginated response wrapper."""

    pagination: dict = Field(default_factory=dict)


# Dependency injection for better testability
async def get_zone_config(config_path: str = "config/hr_zones.json") -> ZoneConfig:
    """Dependency to provide zone configuration."""
    try:
        return ZoneConfig(config_path)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration not found: {config_path}",
        )


# Versioned API
def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    app = FastAPI(
        title="ERG Zone Calculator API",
        description="Calculate training zones for heart rate and pace",
        version="1.0.0",
        docs_url="/v1/docs",
        redoc_url="/v1/redoc",
        openapi_url="/v1/openapi.json",
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# Versioned routes
@app.get("/v1/health", response_model=APIResponse)
async def health_check():
    """Health check with standard response format."""
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "service": "erg-zone-calculator",
            "uptime": "calculate_uptime_here",
        },
    )


@app.post("/v1/zones/hr", response_model=APIResponse)
async def calculate_hr_zones_v1(
    request: HRZoneRequest, config: Annotated[ZoneConfig, Depends(get_zone_config)]
):
    """Calculate HR zones with standard response format."""
    try:
        calculator = HRZoneCalculator(config)
        formatter = HRFormatter()

        # Calculate zones
        all_lower = calculator.calculate_all_lower_bounds(request.max_hr)
        all_upper = calculator.calculate_all_upper_bounds(request.max_hr)

        # Format response
        zones = []
        for zone_name in config.get_zone_names():
            zones.append(
                {
                    "name": zone_name,
                    "lower_bound": all_lower[zone_name],
                    "upper_bound": all_upper[zone_name],
                    "formatted": formatter.format_zone_bounds(
                        all_lower[zone_name], all_upper[zone_name]
                    ),
                }
            )

        return APIResponse(
            success=True,
            data={
                "benchmark": {"max_hr": request.max_hr},
                "zones": zones,
                "zone_count": len(zones),
            },
        )

    except Exception as e:
        logger.error(f"Error calculating HR zones: {e}")
        return APIResponse(success=False, error=str(e))


# Rate limiting (add dependency: pip install slowapi)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.post("/v1/zones/hr/limited")
    @limiter.limit("10/minute")  # Rate limiting
    async def calculate_hr_zones_with_limits(
        request: Request,
        hr_request: HRZoneRequest,
        config: Annotated[ZoneConfig, Depends(get_zone_config)],
    ):
        """Rate-limited HR zone calculation endpoint."""
        # Same implementation as the non-limited version
        return await calculate_hr_zones_v1(hr_request, config)

except ImportError:
    # slowapi not installed, skip rate limiting
    logger.warning("slowapi not installed, rate limiting disabled")
    pass


# Add OpenAPI customization
def custom_openapi():
    """Custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="ERG Zone Calculator API",
        version="1.0.0",
        description="Professional training zone calculator",
        routes=app.routes,
    )

    # Add custom info
    openapi_schema["info"]["contact"] = {
        "name": "API Support",
        "email": "support@example.com",
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
