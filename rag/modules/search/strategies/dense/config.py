"""Dense search strategy configuration."""

from dataclasses import dataclass
from rag.modules.search.config import BaseSearchConfig


@dataclass
class DenseSearchConfig(BaseSearchConfig):
    """Configuration for dense vector search."""
    top_k: int = 5
