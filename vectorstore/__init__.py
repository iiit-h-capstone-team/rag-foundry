"""Vector store module with registry-based strategy architecture."""

from vectorstore.base import VectorStoreStrategy
from vectorstore.registry import vectorstore_registry, VectorStoreRegistry
from vectorstore.enums import VectorStoreType
from vectorstore.config import VectorStoreConfig, BaseVectorStoreConfig

from vectorstore.strategies.faiss.config import FaissVectorStoreConfig

# Eagerly import to trigger @register decorator; guarded for missing faiss
try:
    from vectorstore.strategies.faiss.strategy import FaissVectorStoreStrategy
except ImportError:
    pass


__all__ = [
    "VectorStoreStrategy",
    "VectorStoreRegistry",
    "vectorstore_registry",
    "VectorStoreType",
    "VectorStoreConfig",
    "BaseVectorStoreConfig",
    "FaissVectorStoreConfig",
    "FaissVectorStoreStrategy",
]
