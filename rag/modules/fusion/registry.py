"""Fusion strategy registry."""

from core.registry import BaseRegistry
from rag.modules.fusion.base import FusionStrategy


class FusionRegistry(BaseRegistry[FusionStrategy]):
    """Registry for fusion strategy plugins.
    
    Manages registration and instantiation of fusion strategies.
    """
    pass


fusion_registry = FusionRegistry()
