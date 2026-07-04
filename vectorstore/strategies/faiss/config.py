"""FAISS vector store strategy configuration."""

from dataclasses import dataclass
from vectorstore.config import BaseVectorStoreConfig


@dataclass
class FaissVectorStoreConfig(BaseVectorStoreConfig):
    """Configuration for FAISS vector store."""
    dimension: int = 768
