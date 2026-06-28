from abc import ABC
from abc import abstractmethod


class SearchStrategy(ABC):

    @abstractmethod
    def search(self, query: str) -> list[dict]:
        """Return one ranked list of candidate chunks for the query."""
        pass
