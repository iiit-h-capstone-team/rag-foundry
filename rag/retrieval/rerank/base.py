from abc import ABC
from abc import abstractmethod

from rag.retrieval.context import RetrievalContext


class RetrievalRerankStage(ABC):

    @abstractmethod
    def run(self, ctx: RetrievalContext) -> RetrievalContext:
        """Rerank fused candidates into final retrieved chunks."""
        pass
