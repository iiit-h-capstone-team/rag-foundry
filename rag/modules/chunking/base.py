"""Base chunking strategy class."""

from abc import abstractmethod
import re

from core.strategy import BaseStrategy
from rag.models.document import Document
from rag.models.chunk import Chunk


class ChunkingStrategy(BaseStrategy):
    """Base class for chunking strategies.
    
    Defines the interface for chunking implementations and provides
    shared helper methods for common chunking operations.
    """

    @abstractmethod
    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:
        """Chunk a document into smaller pieces.
        
        Args:
            document: Document to chunk.
            
        Returns:
            List of chunks.
        """
        pass

    @staticmethod
    def split_sentences(text: str) -> list[str]:
        """Split text into sentences.
        
        Args:
            text: Text to split.
            
        Returns:
            List of sentences.
        """
        return [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                text
            )
            if sentence.strip()
        ]