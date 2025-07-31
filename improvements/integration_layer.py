"""
Integration layer to bridge old and new implementations.
"""

from typing import Protocol, runtime_checkable
from abc import abstractmethod


@runtime_checkable
class ZoneConfigProtocol(Protocol):
    """Protocol that both old and new config classes must implement."""
    
    @abstractmethod
    def get_zone_names(self) -> list[str]: ...
    
    @abstractmethod
    def get_lower_bound_coefficient(self, zone: str) -> float: ...
    
    @abstractmethod
    def get_upper_bound_coefficient(self, zone: str) -> float: ...


# Adapter to make old ZoneConfig work with new calculators
class ZoneConfigAdapter:
    """Adapter to bridge old ZoneConfig with new type-safe calculators."""
    
    def __init__(self, old_config):
        self._config = old_config
    
    def get_zone_names(self) -> list[str]:
        return self._config.get_zone_names()
    
    def get_lower_bound_coefficient(self, zone: str) -> float:
        return self._config.get_lower_bound_coefficient(zone)
    
    def get_upper_bound_coefficient(self, zone: str) -> float:
        return self._config.get_upper_bound_coefficient(zone)


# Factory to create the right config type
def create_zone_config(config_path: str, use_optimized: bool = True) -> ZoneConfigProtocol:
    """Factory to create zone config with backward compatibility."""
    if use_optimized:
        from optimized_config import OptimizedZoneConfig
        return OptimizedZoneConfig(config_path)
    else:
        from zone_configs import ZoneConfig
        return ZoneConfigAdapter(ZoneConfig(config_path))