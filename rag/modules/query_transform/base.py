"""Base query transform strategy class."""

from abc import abstractmethod
from dataclasses import dataclass, field

from core.strategy import BaseStrategy


@dataclass
class QueryTransformResult:
    """Result of query transformation with separate dense and sparse query lists."""
    dense_queries: list[str]
    sparse_queries: list[str]
    metadata: dict = field(default_factory=dict)


class QueryTransformStrategy(BaseStrategy):
    """Base class for query transform strategies."""

    @abstractmethod
    def transform(self, query: str) -> QueryTransformResult:
        """Transform the query before search.
        
        Args:
            query: Original user query.
            
        Returns:
            QueryTransformResult with dense_queries and sparse_queries.
        """
        pass
