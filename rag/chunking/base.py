from abc import ABC
from abc import abstractmethod
import re

from rag.models.document import Document
from rag.models.chunk import Chunk

class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:
        pass

    @staticmethod
    def split_sentences(
        text: str
    ):

        return [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                text
            )
            if sentence.strip()
        ]