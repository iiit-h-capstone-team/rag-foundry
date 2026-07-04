"""Search module with registry-based strategy architecture."""

from rag.modules.search.base import SearchStrategy
from rag.modules.search.registry import search_registry, SearchRegistry
from rag.modules.search.enums import SearchType
from rag.modules.search.config import SearchStrategyConfig, SearchPipelineConfig, BaseSearchConfig

from rag.modules.search.strategies.dense.config import DenseSearchConfig
from rag.modules.search.strategies.dense.strategy import DenseSearchStrategy

from rag.modules.search.strategies.sparse.config import SparseSearchConfig
from rag.modules.search.strategies.sparse.strategy import SparseSearchStrategy


__all__ = [
    "SearchStrategy",
    "SearchRegistry",
    "search_registry",
    "SearchType",
    "SearchStrategyConfig",
    "SearchPipelineConfig",
    "BaseSearchConfig",
    "DenseSearchConfig",
    "DenseSearchStrategy",
    "SparseSearchConfig",
    "SparseSearchStrategy",
]
