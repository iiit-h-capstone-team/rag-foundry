from rag.chunking.base import ChunkingStrategy
from rag.models.chunk import Chunk
from rag.models.document import Document


class FixedWindowChunkingStrategy(ChunkingStrategy):

    def __init__(
        self,
        window_size: int = 256,
        overlap: int = 50
    ):
        self.window_size = window_size
        self.overlap = overlap

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

            start = end - self.overlap

        return chunks
