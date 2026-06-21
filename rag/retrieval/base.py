from abc import ABC
from abc import abstractmethod


class RetrievalStrategy(ABC):

    @abstractmethod
    def retrieve(
        self,
        query: str
    ):
        """Retrieve relevant chunks for a query.

        All tunable parameters (top_k, initial_k, weights, ...) are read from
        the strategy's stored config; the query is the only runtime argument.
        """
        pass
