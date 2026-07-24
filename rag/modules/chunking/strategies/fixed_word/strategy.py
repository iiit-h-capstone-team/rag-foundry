"""Fixed-word chunking strategy implementation.

Splits text by whitespace boundaries (words), NOT by actual
tokenizer tokens. For true token-based chunking, use the
``token`` strategy instead.
"""

from rag.modules.chunking.base import ChunkingStrategy
from rag.modules.chunking.registry import chunking_registry
from rag.modules.chunking.enums import ChunkingType
from rag.modules.chunking.strategies.fixed_word.config import FixedWordChunkingConfig
from rag.models.chunk import Chunk
from rag.models.document import Document


@chunking_registry.register(ChunkingType.FIXED_WORD)
class FixedWordChunkingStrategy(ChunkingStrategy):
    """Chunking strategy based on word count (whitespace split)."""

    def __init__(self, config: FixedWordChunkingConfig):
        super().__init__(config)

    @property
    def max_words(self) -> int:
        return self.config.max_words

    @property
    def overlap_words(self) -> int:
        return self.config.overlap_words

    def chunk(self, document: Document) -> list[Chunk]:
        words = document.content.split()
        chunks = []
        i = 0

        while i < len(words):

            chunk_words = words[i : i + self.max_words]
            chunk_text = " ".join(chunk_words)

            chunk = Chunk(
                text=chunk_text,
                metadata={
                    **document.metadata,
                    "chunk_type": "fixed_word",
                    "word_count": len(chunk_words),
                    "title": document.title,
                },
            )
            chunks.append(chunk)

            i += self.max_words - self.overlap_words

        return chunks
