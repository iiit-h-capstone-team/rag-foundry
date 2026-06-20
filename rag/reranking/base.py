from abc import ABC
from abc import abstractmethod


class RerankerStrategy(ABC):

    @abstractmethod
    def rerank(
        self,
        query,
        texts
    ):
        """Return a relevance score for each text given the query."""
        pass
