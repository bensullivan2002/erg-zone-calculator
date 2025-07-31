"""
Production-ready API with all the bells and whistles.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated, Optional
from datetime import datetime, timedelta
import logging
import time
import uuid
from contextlib import asynccontextmanager

# Metrics and monitoring
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"]
)
REQUEST_DURATION = Histogram("http_request_duration_seconds", "HTTP request duration")
CALCULATION_COUNT = Counter(
    "zone_calculations_total", "Total zone calculations", ["type"]
)
CALCULATION_ERRORS = Counter(
    "zone_calculation_errors_total", "Zone calculation errors", ["type", "error"]
)


# Enhanced response models
class APIMetadata(BaseModel):
    """API metadata for responses."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "2.0.0"
    processing_time_ms: Optional[float] = None


class APIResponse(BaseModel):
    """Enhanced API response with metadata."""

    success: bool
    data: dict | list | None = None
    error: Optional[str] = None
    metadata: APIMetadata = Field(default_factory=APIMetadata)


class HealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    dependencies: dict[str, str]
    metrics: dict[str, int | float]


# Security
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """Verify API key for protected endpoints."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="API key required"
        )

    # In production, verify against database/cache
    valid_keys = {"test-key-123", "prod-key-456"}  # Load from env/config

    if credentials.credentials not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    return credentials.credentials


# Application lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    # Startup
    logger.info("Starting ERG Zone Calculator API")
    app.state.start_time = time.time()

    # Health checks for dependencies
    try:
        # Test config loading
        from optimized_config import OptimizedZoneConfig

        test_config = OptimizedZoneConfig("config/hr_zones.json")
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down ERG Zone Calculator API")


def create_production_app() -> FastAPI:
    """Create production-ready FastAPI application."""
    app = FastAPI(
        title="ERG Zone Calculator API",
        description="Production-ready training zone calculator with monitoring, security, and observability",
        version="2.0.0",
        docs_url="/v2/docs",
        redoc_url="/v2/redoc",
        openapi_url="/v2/openapi.json",
        lifespan=lifespan,
    )

    # Security middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "*.example.com"],  # Configure for production
    )

    # Performance middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # CORS with proper configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://app.example.com"],  # Specific origins in production
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=3600,
    )

    return app


app = create_production_app()


# Middleware for request tracking and metrics
@app.middleware("http")
async def track_requests(request: Request, call_next):
    """Track requests for metrics and logging."""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    # Add request ID to logs
    logger.bind(request_id=request_id)

    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method, endpoint=request.url.path, status=response.status_code
    ).inc()

    REQUEST_DURATION.observe(process_time)

    # Add headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Health and monitoring endpoints
@app.get("/v2/health", response_model=HealthResponse)
async def detailed_health_check():
    """Comprehensive health check with dependency status."""
    uptime = time.time() - app.state.start_time

    # Check dependencies
    dependencies = {}
    try:
        from optimized_config import OptimizedZoneConfig

        OptimizedZoneConfig("config/hr_zones.json")
        dependencies["config"] = "healthy"
    except Exception:
        dependencies["config"] = "unhealthy"

    return HealthResponse(
        status="healthy"
        if all(v == "healthy" for v in dependencies.values())
        else "degraded",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        uptime_seconds=uptime,
        dependencies=dependencies,
        metrics={
            "total_requests": REQUEST_COUNT._value.sum(),
            "avg_response_time": REQUEST_DURATION._sum.sum()
            / max(REQUEST_DURATION._count.sum(), 1),
            "total_calculations": CALCULATION_COUNT._value.sum(),
            "calculation_errors": CALCULATION_ERRORS._value.sum(),
        },
    )


@app.get("/v2/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Protected calculation endpoints
@app.post("/v2/zones/hr", response_model=APIResponse)
async def calculate_hr_zones_v2(
    request: HRZoneRequest,
    background_tasks: BackgroundTasks,
    api_key: Annotated[str, Depends(verify_api_key)],
):
    """Calculate HR zones with full production features."""
    start_time = time.time()
    request_id = str(uuid.uuid4())

    try:
        logger.info(
            "HR zone calculation started",
            request_id=request_id,
            max_hr=request.max_hr,
            api_key=api_key[:8] + "...",
        )

        # Use dependency injection
        from dependency_injection import get_service
        from type_safe_calculators import HRZoneCalculator, HRBenchmark
        from zone_formatters import HRFormatter

        calculator = get_service(HRZoneCalculator)
        formatter = get_service(HRFormatter)

        # Create type-safe benchmark
        benchmark = HRBenchmark(max_hr=request.max_hr)

        # Calculate zones
        zones_data = []
        for zone_name in calculator.zone_config.get_zone_names():
            lower = calculator.calculate_lower_bound(zone_name, benchmark)
            upper = calculator.calculate_upper_bound(zone_name, benchmark)

            zones_data.append(
                {
                    "name": zone_name,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "formatted": formatter.format_zone_bounds(lower, upper),
                }
            )

        # Record success metrics
        CALCULATION_COUNT.labels(type="hr").inc()

        # Background task for analytics
        background_tasks.add_task(
            log_calculation_analytics,
            "hr",
            request.max_hr,
            len(zones_data),
            time.time() - start_time,
        )

        processing_time = (time.time() - start_time) * 1000

        return APIResponse(
            success=True,
            data={
                "benchmark": {"max_hr": request.max_hr},
                "zones": zones_data,
                "zone_count": len(zones_data),
            },
            metadata=APIMetadata(
                request_id=request_id, processing_time_ms=processing_time
            ),
        )

    except Exception as e:
        CALCULATION_ERRORS.labels(type="hr", error=type(e).__name__).inc()
        logger.error(
            "HR zone calculation failed",
            request_id=request_id,
            error=str(e),
            exc_info=True,
        )

        return APIResponse(
            success=False,
            error=f"Calculation failed: {str(e)}",
            metadata=APIMetadata(request_id=request_id),
        )


async def log_calculation_analytics(
    calc_type: str, benchmark_value: float, zone_count: int, duration: float
):
    """Background task to log calculation analytics."""
    logger.info(
        "Calculation analytics",
        type=calc_type,
        benchmark_value=benchmark_value,
        zone_count=zone_count,
        duration_seconds=duration,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "production_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable in production
        access_log=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["default"],
            },
        },
    )
