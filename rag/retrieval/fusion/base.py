from abc import ABC
from abc import abstractmethod

from rag.retrieval.context import RetrievalContext


class FusionStrategy(ABC):

    @abstractmethod
    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        """Combine search result lists into a single ranked list."""
        pass
