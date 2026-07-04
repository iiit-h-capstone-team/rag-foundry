"""Vector store strategy registry."""

from core.registry import BaseRegistry
from vectorstore.base import VectorStoreStrategy


class VectorStoreRegistry(BaseRegistry[VectorStoreStrategy]):
    """Registry for vector store strategy plugins.
    
    Manages registration and instantiation of vector store strategies.
    """
    pass


vectorstore_registry = VectorStoreRegistry()
