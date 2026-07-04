"""Search strategy registry."""

from core.registry import BaseRegistry
from rag.modules.search.base import SearchStrategy


class SearchRegistry(BaseRegistry[SearchStrategy]):
    """Registry for search strategy plugins.
    
    Manages registration and instantiation of search strategies.
    """
    pass


search_registry = SearchRegistry()
