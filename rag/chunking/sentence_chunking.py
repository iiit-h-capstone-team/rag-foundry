import re

from rag.chunking.base import ChunkingStrategy
from rag.config.config import SentenceChunkingConfig
from rag.models.chunk import Chunk
from rag.models.document import Document

class SentenceChunkingStrategy(
    ChunkingStrategy
):

    def __init__(
        self,
        config: SentenceChunkingConfig
    ):
        self.config = config

    @property
    def max_words(self) -> int:
        return self.config.max_words

    @property
    def overlap_sentences(self) -> int:
        return self.config.overlap_sentences
    
    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:

        sentences = ChunkingStrategy.split_sentences(
            document.content
        )

        chunk_texts = []
        current_chunk = []
        current_words = 0

        i = 0
        while i < len(sentences):

            sentence = sentences[i]
            sentence_words = len(sentence.split())

            # Oversized single sentence: flush current chunk, store it alone.
            if sentence_words > self.max_words:

                if current_chunk:
                    chunk_texts.append(" ".join(current_chunk))
                    current_chunk = []
                    current_words = 0

                chunk_texts.append(sentence)
                i += 1
                continue

            # Overflow: close current chunk and seed the next one with overlap.
            if current_words + sentence_words > self.max_words:

                if current_chunk:
                    chunk_texts.append(" ".join(current_chunk))

                overlap = (
                    current_chunk[-self.overlap_sentences:]
                    if self.overlap_sentences > 0 else []
                )

                current_chunk = overlap
                current_words = sum(len(s.split()) for s in current_chunk)

                if current_words + sentence_words > self.max_words:
                    current_chunk = []
                    current_words = 0

                continue

            current_chunk.append(sentence)
            current_words += sentence_words
            i += 1

        if current_chunk:
            chunk_texts.append(" ".join(current_chunk))

        return [
            Chunk(
                text=text,
                metadata={
                    **document.metadata,
                    "chunk_type": "sentence_based",
                    "word_count": len(text.split()),
                    "title": document.title
                }
            )
            for text in chunk_texts
        ]