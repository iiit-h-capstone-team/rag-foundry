"""Vector store strategy types."""

from enum import Enum


class VectorStoreType(str, Enum):
    """Available vector store strategies."""
    FAISS = "faiss"
