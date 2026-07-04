"""Voyage AI embedding strategy implementation."""

import os

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.voyage.config import VoyageEmbeddingConfig


@embedding_registry.register(EmbeddingType.VOYAGE)
class VoyageEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using Voyage AI API."""

    DEFAULT_MODEL = "voyage-large-2"

    def __init__(self, config: VoyageEmbeddingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            import voyageai
            api_key = os.environ.get("VOYAGE_API_KEY")
            if not api_key:
                raise ValueError(
                    "VOYAGE_API_KEY environment variable is required for VoyageEmbeddingStrategy"
                )
            voyageai.api_key = api_key
            self._client = voyageai.Client()
        return self._client

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if self.config.input_type:
            response = self._client.embed(
                texts=texts, model=self.model, input_type=self.config.input_type
            )
        else:
            response = self._client.embed(texts=texts, model=self.model)

        return response.embeddings
