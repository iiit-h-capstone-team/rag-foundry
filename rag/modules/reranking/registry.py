"""Reranking strategy registry."""

from core.registry import BaseRegistry
from rag.modules.reranking.base import RerankerStrategy


class RerankingRegistry(BaseRegistry[RerankerStrategy]):
    """Registry for reranking strategy plugins.
    
    Manages registration and instantiation of reranking strategies.
    """
    pass


reranking_registry = RerankingRegistry()
