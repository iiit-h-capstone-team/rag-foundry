"""Sentence Transformer embedding strategy implementation."""

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.sentence_transformer.config import SentenceTransformerEmbeddingConfig
from rag.runtime.model_cache import get_sentence_transformer


@embedding_registry.register(EmbeddingType.SENTENCE_TRANSFORMER)
class SentenceTransformerEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using Sentence Transformers."""

    def __init__(self, config: SentenceTransformerEmbeddingConfig):
        super().__init__(config)

        model_name = self.config.model_name or self.config.model
        if not model_name:
            raise ValueError(
                "SentenceTransformerEmbeddingStrategy requires "
                "'model_name' (or 'model') in the embedding config."
            )

        self.model = get_sentence_transformer(model_name)

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        return self.model.encode(texts, normalize_embeddings=True)
