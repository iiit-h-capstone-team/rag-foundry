"""Sparse search strategy configuration."""

from dataclasses import dataclass
from rag.modules.search.config import BaseSearchConfig


@dataclass
class SparseSearchConfig(BaseSearchConfig):
    """Configuration for sparse (BM25) search."""
    top_k: int = 5
