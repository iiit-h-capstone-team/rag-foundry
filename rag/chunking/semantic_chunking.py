import numpy as np

from rag.chunking.base import ChunkingStrategy
from rag.config.config import SemanticChunkingConfig
from rag.embedding.embedding_factory import EmbeddingFactory
from rag.models.chunk import Chunk
from rag.models.document import Document


class SemanticChunkingStrategy(ChunkingStrategy):

    def __init__(self, config: SemanticChunkingConfig):
        self.config = config
        self.embedding = EmbeddingFactory.create_embedder(
            config.embedding
        )

    @property
    def max_words(self) -> int:
        return self.config.max_words

    @property
    def similarity_threshold(self) -> float:
        return self.config.similarity_threshold

    @property
    def similarity_window(self) -> int:
        return self.config.similarity_window

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

        if not sentences:
            return []

        embeddings = np.asarray(
            self.embedding.embed(sentences),
            dtype=np.float32,
        )

        # Normalize embeddings once so cosine similarity
        # becomes a simple dot product.
        norms = np.linalg.norm(
            embeddings,
            axis=1,
            keepdims=True,
        )
        embeddings /= np.maximum(norms, 1e-12)

        chunk_texts = []
        current_chunk = []
        current_words = 0

        i = 0

        while i < len(sentences):

            sentence = sentences[i]
            sentence_words = len(sentence.split())

            # Handle oversized sentence.
            if sentence_words > self.max_words:

                if current_chunk:
                    chunk_texts.append(
                        " ".join(current_chunk)
                    )
                    current_chunk = []
                    current_words = 0

                chunk_texts.append(sentence)
                i += 1
                continue

            should_split = False

            if current_chunk:

                # Split immediately if adding this sentence
                # exceeds the configured chunk size.
                if current_words + sentence_words > self.max_words:
                    should_split = True

                else:
                    start = max(
                        0,
                        i - self.similarity_window
                    )

                    reference_embedding = embeddings[
                        start:i
                    ].mean(axis=0)

                    norm = np.linalg.norm(
                        reference_embedding
                    )

                    if norm > 0:
                        reference_embedding /= norm

                    similarity = np.dot(
                        reference_embedding,
                        embeddings[i],
                    )

                    if similarity < self.similarity_threshold:
                        should_split = True

            if should_split:

                chunk_texts.append(
                    " ".join(current_chunk)
                )

                overlap = (
                    current_chunk[-self.overlap_sentences:]
                    if self.overlap_sentences > 0
                    else []
                )

                current_chunk = overlap

                current_words = sum(
                    len(s.split())
                    for s in current_chunk
                )

            current_chunk.append(sentence)
            current_words += sentence_words

            i += 1

        if current_chunk:
            chunk_texts.append(
                " ".join(current_chunk)
            )

        return [
            Chunk(
                text=text,
                metadata={
                    **document.metadata,
                    "chunk_type": "semantic",
                    "word_count": len(text.split()),
                    "title": document.title,
                },
            )
            for text in chunk_texts
        ]