"""Provider strategy registry."""

from core.registry import BaseRegistry
from providers.base.strategy import ProviderStrategy


class ProviderRegistry(BaseRegistry[ProviderStrategy]):
    """Registry for LLM provider strategy plugins.
    
    Manages registration and instantiation of provider strategies.
    """
    pass


provider_registry = ProviderRegistry()
