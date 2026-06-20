import re
from rag.chunking.base import ChunkingStrategy
from rag.models.chunk import Chunk
from rag.models.document import Document


class TokenChunkingStrategy(ChunkingStrategy):

    def __init__(
        self,
        max_tokens: int = 200,
        overlap_tokens: int = 20
    ):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:

        words = document.content.split()
        chunks = []
        i = 0

        while i < len(words):

            chunk_words = words[i:i + self.max_tokens]
            chunk_text = " ".join(chunk_words)

            chunk = Chunk(
                text=chunk_text,
                metadata={
                    **document.metadata,
                    "chunk_type": "token_based",
                    "token_count": len(chunk_words),
                    "title": document.title
                }
            )
            chunks.append(chunk)

            i += self.max_tokens - self.overlap_tokens

        return chunks
