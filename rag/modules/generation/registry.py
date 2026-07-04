"""Generation strategy registry."""

from core.registry import BaseRegistry
from rag.modules.generation.base import GenerationStrategy


class GenerationRegistry(BaseRegistry[GenerationStrategy]):
    """Registry for generation strategy plugins.
    
    Manages registration and instantiation of generation strategies.
    """
    pass


generation_registry = GenerationRegistry()
