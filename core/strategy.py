"""Base strategy class for plugin architecture."""

from typing import Generic, TypeVar

T = TypeVar("T")


class BaseStrategy(Generic[T]):
    """Generic base class for all strategies.
    
    Stores configuration and provides a foundation for domain-specific
    strategy implementations. Each derived strategy exposes its own API
    (e.g., chunk(), embed(), retrieve(), generate(), rerank()).
    """

    def __init__(self, config: T):
        """Initialize strategy with configuration.
        
        Args:
            config: Strategy-specific configuration object.
        """
        self.config = config
