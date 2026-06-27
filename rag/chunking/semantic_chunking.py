from rag.config.config import SemanticChunkingConfig
from rag.factory.strategy_factory import StrategyFactory
from rag.models import Document, Chunk
import numpy as np


class SemanticChunkingStrategy(ChunkingStrategy):

    def __init__(self, config: SemanticChunkingConfig):
        self.config = config
        self.embedding = StrategyFactory.create_embedding(
            config.embedding
        )

    def chunk(
        self,
        document: Document
    ) -> list[Chunk]:

        sentences = self.split_sentences(
            document.content
        )

        if not sentences:
            return []

        embeddings = np.asarray(
            self.embedding.embed(sentences)
        )

        chunk_texts = []
        current_chunk = []
        current_words = 0

        i = 0

        while i < len(sentences):

            sentence = sentences[i]
            sentence_words = len(sentence.split())

            # Oversized single sentence.
            if sentence_words > self.max_words:

                if current_chunk:
                    chunk_texts.append(" ".join(current_chunk))
                    current_chunk = []
                    current_words = 0

                chunk_texts.append(sentence)
                i += 1
                continue

            should_split = False

            if current_chunk:

                start = max(
                    0,
                    i - self.similarity_window
                )

                reference_embedding = embeddings[start:i].mean(
                    axis=0
                )
                reference_embedding /= np.linalg.norm(reference_embedding)

                similarity = np.dot(
                    reference_embedding,
                    embeddings[i]
                )

                if similarity < self.similarity_threshold:
                    should_split = True

                elif (
                    current_words + sentence_words
                    > self.max_words
                ):
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
                }
            )
            for text in chunk_texts
        ]