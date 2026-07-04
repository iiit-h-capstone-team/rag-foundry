"""Cohere embedding strategy implementation."""

import os

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.cohere.config import CohereEmbeddingConfig


@embedding_registry.register(EmbeddingType.COHERE)
class CohereEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using Cohere API."""

    DEFAULT_MODEL = "embed-english-v3"

    def __init__(self, config: CohereEmbeddingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import cohere
            api_key = os.environ.get("COHERE_API_KEY")
            if not api_key:
                raise ValueError(
                    "COHERE_API_KEY environment variable is required for CohereEmbeddingStrategy"
                )
            self._client = cohere.Client(api_key=api_key)
        return self._client

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embed(
            texts=texts, model=self.model, input_type=self.config.input_type
        )

        return response.embeddings
