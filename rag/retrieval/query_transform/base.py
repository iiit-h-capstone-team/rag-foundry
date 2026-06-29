from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass, field

from rag.retrieval.context import RetrievalContext


@dataclass
class QueryTransformResult:
    """Result of query transformation with separate dense and sparse query lists."""
    dense_queries: list[str]
    sparse_queries: list[str]
    metadata: dict = field(default_factory=dict)


class QueryTransformStrategy(ABC):

    @abstractmethod
    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        """Transform the query before search.
        
        Strategies should set ctx.dense_queries and ctx.sparse_queries
        to control which queries are used for dense and sparse retrieval.
        """
        pass
