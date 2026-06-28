from abc import ABC
from abc import abstractmethod

from rag.retrieval.context import RetrievalContext


class QueryTransformStrategy(ABC):

    @abstractmethod
    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        """Transform the query before search."""
        pass
