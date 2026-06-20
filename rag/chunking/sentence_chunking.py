import re

from rag.chunking.base import ChunkingStrategy
from rag.models.chunk import Chunk
from rag.models.document import Document

class SentenceChunkingStrategy(
    ChunkingStrategy
):

    def __init__(
        self,
        max_words=100,
        overlap_sentences=1
    ):

        self.max_words = max_words

        self.overlap_sentences = overlap_sentences

    def split_sentences(
        self,
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
    
    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:

        sentences = self.split_sentences(
            document.content
        )

        chunks = []

        # your existing chunk logic

        return chunks