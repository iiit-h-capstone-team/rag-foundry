"""Fixed-window chunking strategy implementation."""

from rag.modules.chunking.base import ChunkingStrategy
from rag.modules.chunking.registry import chunking_registry
from rag.modules.chunking.enums import ChunkingType
from rag.modules.chunking.strategies.fixed_window.config import FixedWindowChunkingConfig
from rag.models.chunk import Chunk
from rag.models.document import Document


@chunking_registry.register(ChunkingType.FIXED_WINDOW)
class FixedWindowChunkingStrategy(ChunkingStrategy):
    """Chunking strategy using fixed-size windows."""

    def __init__(self, config: FixedWindowChunkingConfig):
        super().__init__(config)

    @property
    def window_size(self) -> int:
        return self.config.window_size

    @property
    def overlap(self) -> int:
        return self.config.overlap

    def chunk(self, document: Document) -> list[Chunk]:
        text = document.content
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.window_size, len(text))
            chunk_text = text[start:end]

            chunk = Chunk(
                text=chunk_text.strip(),
                metadata={
                    **document.metadata,
                    "chunk_type": "fixed_window",
                    "start_pos": start,
                    "end_pos": end,
                    "title": document.title,
                },
            )
            chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks
