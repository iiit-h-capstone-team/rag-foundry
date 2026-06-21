from rag.chunking.base import ChunkingStrategy
from rag.config.config import FixedWindowChunkingConfig
from rag.models.chunk import Chunk
from rag.models.document import Document


class FixedWindowChunkingStrategy(ChunkingStrategy):

    def __init__(
        self,
        config: FixedWindowChunkingConfig
    ):
        self.config = config

    @property
    def window_size(self) -> int:
        return self.config.window_size

    @property
    def overlap(self) -> int:
        return self.config.overlap

    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:

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
                    "title": document.title
                }
            )
            chunks.append(chunk)

            if end >= len(text):
                break

            start = end - self.overlap

        return chunks
