"""
Pydantic models for API request/response validation.
"""

from typing import ClassVar
from pydantic import BaseModel, Field, ConfigDict

from app.src.constants import HeartRateValidation, PaceValidation


class HRZoneRequest(BaseModel):
    """Request model for HR zone calculations."""

    max_hr: int = Field(
        ...,
        ge=HeartRateValidation.MIN_HEART_RATE,
        le=HeartRateValidation.MAX_HEART_RATE,
        description="Maximum heart rate in BPM",
    )
    config_path: str = Field(
        default="app/config/hr_zones.json", description="Path to HR zone configuration file"
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(
        {
            "json_schema_extra": {
                "example": {"max_hr": 185, "config_path": "app/config/hr_zones.json"}
            }
        }
    )


class PaceZoneRequest(BaseModel):
    """Request model for pace zone calculations."""

    distance_meters: int = Field(
        ...,
        ge=PaceValidation.MIN_DISTANCE_METERS,
        le=PaceValidation.MAX_DISTANCE_METERS,
        description="Distance in meters",
    )
    time_seconds: float = Field(
        ..., ge=PaceValidation.MIN_TIME_SECONDS, le=PaceValidation.MAX_TIME_SECONDS, description="Time in seconds"
    )
    config_path: str = Field(
        default="app/config/pace_zones.json",
        description="Path to pace zone configuration file",
    )

    model_config: ClassVar[ConfigDict] = ConfigDict(
        {
            "json_schema_extra": {
                "example": {
                    "distance_meters": 2000,
                    "time_seconds": 415.0,
                    "config_path": "app/config/pace_zones.json",
                }
            }
        }
    )


class ZoneResult(BaseModel):
    """Individual zone calculation result."""

    zone_name: str = Field(..., description="Name of the training zone")
    lower_bound: int | float | None = Field(
        ..., description="Lower bound numeric value or None for open-ended"
    )
    upper_bound: int | float | None = Field(
        ..., description="Upper bound numeric value or None for open-ended"
    )
    lower_bound_formatted: str = Field(
        ..., description="Lower bound formatted for display"
    )
    upper_bound_formatted: str = Field(
        ..., description="Upper bound formatted for display"
    )
    range_formatted: str = Field(..., description="Full range formatted for display")


class HRZoneResponse(BaseModel):
    """Response model for HR zone calculations."""

    max_hr: int = Field(..., description="Maximum heart rate used for calculations")
    zones: list[ZoneResult] = Field(..., description="List of calculated zones")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        {
            "json_schema_extra": {
                "example": {
                    "max_hr": 185,
                    "zones": [
                        {
                            "zone_name": "Zone 1",
                            "lower_bound": 92,
                            "upper_bound": 111,
                            "lower_bound_formatted": "92bpm",
                            "upper_bound_formatted": "111bpm",
                            "range_formatted": "92bpm-111bpm",
                        }
                    ],
                }
            }
        }
    )


class PaceZoneResponse(BaseModel):
    """Response model for pace zone calculations."""

    distance_meters: int = Field(..., description="Distance used for calculations")
    time_seconds: float = Field(..., description="Time used for calculations")
    benchmark_pace: str = Field(..., description="Benchmark pace formatted")
    zones: list[ZoneResult] = Field(..., description="List of calculated zones")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        {
            "json_schema_extra": {
                "example": {
                    "distance_meters": 2000,
                    "time_seconds": 415.0,
                    "benchmark_pace": "1:43/500m",
                    "zones": [
                        {
                            "zone_name": "UT2",
                            "lower_bound": 122.5,
                            "upper_bound": 128.7,
                            "lower_bound_formatted": "2:02/500m",
                            "upper_bound_formatted": "2:08/500m",
                            "range_formatted": "2:02/500m-2:08/500m",
                        }
                    ],
                }
            }
        }
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")

    model_config: ClassVar[ConfigDict] = ConfigDict(
        {
            "json_schema_extra": {
                "example": {
                    "error": "Configuration file not found",
                    "detail": "Config file not found at app/config/hr_zones.json",
                }
            }
        }
    )
