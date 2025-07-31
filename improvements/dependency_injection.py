"""
Dependency injection container for better testability and flexibility.
"""

from typing import TypeVar, Generic, Callable, Dict, Any
from abc import ABC, abstractmethod
import inspect


T = TypeVar('T')


class DIContainer:
    """Simple dependency injection container."""
    
    def __init__(self):
        self._services: Dict[type, Any] = {}
        self._factories: Dict[type, Callable] = {}
        self._singletons: Dict[type, Any] = {}
    
    def register_singleton(self, interface: type, implementation: Any) -> None:
        """Register a singleton service."""
        self._singletons[interface] = implementation
    
    def register_factory(self, interface: type, factory: Callable) -> None:
        """Register a factory function."""
        self._factories[interface] = factory
    
    def register_transient(self, interface: type, implementation: type) -> None:
        """Register a transient service (new instance each time)."""
        self._services[interface] = implementation
    
    def resolve(self, interface: type) -> Any:
        """Resolve a service by its interface."""
        # Check singletons first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check factories
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check transient services
        if interface in self._services:
            implementation = self._services[interface]
            return self._create_instance(implementation)
        
        raise ValueError(f"Service {interface} not registered")
    
    def _create_instance(self, cls: type) -> Any:
        """Create instance with dependency injection."""
        signature = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
            
            if param.annotation != inspect.Parameter.empty:
                kwargs[param_name] = self.resolve(param.annotation)
        
        return cls(**kwargs)


# Usage example:
def setup_container() -> DIContainer:
    """Setup the DI container with all services."""
    container = DIContainer()
    
    # Register config
    from optimized_config import OptimizedZoneConfig
    from zone_formatters import HRFormatter, PaceFormatter
    
    container.register_factory(
        OptimizedZoneConfig,
        lambda: OptimizedZoneConfig("config/hr_zones.json")
    )
    
    # Register formatters as singletons
    container.register_singleton(HRFormatter, HRFormatter())
    container.register_singleton(PaceFormatter, PaceFormatter())
    
    # Register calculators as transient
    from type_safe_calculators import HRZoneCalculator, PaceZoneCalculator
    container.register_transient(HRZoneCalculator, HRZoneCalculator)
    container.register_transient(PaceZoneCalculator, PaceZoneCalculator)
    
    return container


# Global container instance
_container = setup_container()

def get_service(interface: type) -> Any:
    """Get service from global container."""
    return _container.resolve(interface)