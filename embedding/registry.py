"""Embedding strategy registry."""

from core.registry import BaseRegistry
from embedding.base import EmbeddingStrategy


class EmbeddingRegistry(BaseRegistry[EmbeddingStrategy]):
    """Registry for embedding strategy plugins.
    
    Manages registration and instantiation of embedding strategies.
    """
    pass


embedding_registry = EmbeddingRegistry()
