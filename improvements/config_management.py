"""
Centralized configuration management with environment support.
"""

from pydantic import BaseSettings, Field, validator
from typing import Optional, Dict, Any
from pathlib import Path
import os


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    host: str = Field(default="localhost", env="DB_HOST")
    port: int = Field(default=5432, env="DB_PORT")
    username: str = Field(default="postgres", env="DB_USERNAME")
    password: str = Field(default="", env="DB_PASSWORD")
    database: str = Field(default="erg_zones", env="DB_DATABASE")
    
    @property
    def url(self) -> str:
        """Database connection URL."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis configuration for caching."""
    host: str = Field(default="localhost", env="REDIS_HOST")
    port: int = Field(default=6379, env="REDIS_PORT")
    password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    db: int = Field(default=0, env="REDIS_DB")
    
    @property
    def url(self) -> str:
        """Redis connection URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ZoneConfig(BaseSettings):
    """Zone calculation configuration."""
    hr_zones_path: str = Field(default="config/hr_zones.json", env="HR_ZONES_CONFIG")
    pace_zones_path: str = Field(default="config/pace_zones.json", env="PACE_ZONES_CONFIG")
    cache_ttl_seconds: int = Field(default=3600, env="ZONE_CACHE_TTL")
    
    @validator('hr_zones_path', 'pace_zones_path')
    def validate_config_paths(cls, v):
        """Validate that config files exist."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Configuration file not found: {v}")
        return str(path.resolve())


class APIConfig(BaseSettings):
    """API configuration."""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=False, env="API_RELOAD")
    
    # Security
    api_keys: list[str] = Field(default_factory=list, env="API_KEYS")
    cors_origins: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    trusted_hosts: list[str] = Field(default=["*"], env="TRUSTED_HOSTS")
    
    # Rate limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    @validator('api_keys', pre=True)
    def parse_api_keys(cls, v):
        """Parse comma-separated API keys."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(',') if key.strip()]
        return v
    
    @validator('cors_origins', 'trusted_hosts', pre=True)
    def parse_lists(cls, v):
        """Parse comma-separated lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")  # json or text
    file_path: Optional[str] = Field(default=None, env="LOG_FILE")
    
    @validator('level')
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    # Tracing
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")
    jaeger_endpoint: Optional[str] = Field(default=None, env="JAEGER_ENDPOINT")
    
    # Health checks
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")


class AppConfig(BaseSettings):
    """Main application configuration."""
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    zones: ZoneConfig = Field(default_factory=ZoneConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment."""
        valid_envs = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_envs:
            raise ValueError(f"Invalid environment: {v}. Must be one of {valid_envs}")
        return v.lower()
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global configuration instance
_config: Optional[AppConfig] = None

def get_config() -> AppConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = AppConfig()
    return _config


def reload_config() -> AppConfig:
    """Reload configuration (useful for testing)."""
    global _config
    _config = AppConfig()
    return _config


# Environment-specific configuration loading
def load_config_for_environment(env: str) -> AppConfig:
    """Load configuration for specific environment."""
    env_file = f".env.{env}"
    if Path(env_file).exists():
        return AppConfig(_env_file=env_file)
    return AppConfig()


# Configuration validation
def validate_config() -> Dict[str, Any]:
    """Validate all configuration and return status."""
    config = get_config()
    status = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Validate zone config files exist
        if not Path(config.zones.hr_zones_path).exists():
            status["errors"].append(f"HR zones config not found: {config.zones.hr_zones_path}")
        
        if not Path(config.zones.pace_zones_path).exists():
            status["errors"].append(f"Pace zones config not found: {config.zones.pace_zones_path}")
        
        # Validate API keys in production
        if config.is_production and not config.api.api_keys:
            status["errors"].append("API keys must be configured in production")
        
        # Validate CORS origins in production
        if config.is_production and "*" in config.api.cors_origins:
            status["warnings"].append("Wildcard CORS origins not recommended in production")
        
        status["valid"] = len(status["errors"]) == 0
        
    except Exception as e:
        status["valid"] = False
        status["errors"].append(f"Configuration validation failed: {str(e)}")
    
    return status