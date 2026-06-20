from abc import ABC
from abc import abstractmethod

class EmbeddingStrategy(ABC):

    @abstractmethod
    def embed(
        self,
        texts
    ):
        pass