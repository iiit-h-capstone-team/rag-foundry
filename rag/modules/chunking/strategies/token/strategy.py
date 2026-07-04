"""Token-based chunking strategy implementation."""

from rag.modules.chunking.base import ChunkingStrategy
from rag.modules.chunking.registry import chunking_registry
from rag.modules.chunking.enums import ChunkingType
from rag.modules.chunking.strategies.token.config import TokenChunkingConfig
from rag.models.chunk import Chunk
from rag.models.document import Document


@chunking_registry.register(ChunkingType.TOKEN)
class TokenChunkingStrategy(ChunkingStrategy):
    """Chunking strategy based on token count."""

    def __init__(self, config: TokenChunkingConfig):
        super().__init__(config)

    @property
    def max_tokens(self) -> int:
        return self.config.max_tokens

    @property
    def overlap_tokens(self) -> int:
        return self.config.overlap_tokens

    def count_tokens(self, text: str) -> int:
        return len(text.split())

    def chunk(self, document: Document) -> list[Chunk]:
        words = document.content.split()
        chunks = []
        i = 0

        while i < len(words):

            chunk_words = words[i : i + self.max_tokens]
            chunk_text = " ".join(chunk_words)

            chunk = Chunk(
                text=chunk_text,
                metadata={
                    **document.metadata,
                    "chunk_type": "token_based",
                    "token_count": len(chunk_words),
                    "title": document.title,
                },
            )
            chunks.append(chunk)

            i += self.max_tokens - self.overlap_tokens

        return chunks
