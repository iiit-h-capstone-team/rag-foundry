"""Chunking strategy registry."""

from core.registry import BaseRegistry
from rag.modules.chunking.base import ChunkingStrategy


class ChunkingRegistry(BaseRegistry[ChunkingStrategy]):
    """Registry for chunking strategy plugins.
    
    Manages registration and instantiation of chunking strategies.
    """
    pass


chunking_registry = ChunkingRegistry()
