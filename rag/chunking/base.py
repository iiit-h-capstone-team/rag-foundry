from abc import ABC
from abc import abstractmethod

from rag.models.document import Document
from rag.models.chunk import Chunk

class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:
        pass