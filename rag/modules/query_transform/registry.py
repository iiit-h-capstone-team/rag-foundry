"""Query transform strategy registry."""

from core.registry import BaseRegistry
from rag.modules.query_transform.base import QueryTransformStrategy


class QueryTransformRegistry(BaseRegistry[QueryTransformStrategy]):
    """Registry for query transform strategy plugins.
    
    Manages registration and instantiation of query transform strategies.
    """
    pass


query_transform_registry = QueryTransformRegistry()
