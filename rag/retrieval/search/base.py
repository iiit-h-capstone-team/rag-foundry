from abc import ABC
from abc import abstractmethod


class SearchStrategy(ABC):

    @abstractmethod
    def search(self, queries: list[str]) -> list[dict]:
        """Return one ranked list of candidate chunks for the queries.
        
        Accepts a list of queries and merges results from all queries,
        deduplicating by chunk index and keeping the best score per chunk.
        """
        pass
