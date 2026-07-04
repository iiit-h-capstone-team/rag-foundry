"""Ollama embedding strategy implementation."""

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.ollama.config import OllamaEmbeddingConfig


@embedding_registry.register(EmbeddingType.OLLAMA)
class OllamaEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using Ollama."""

    DEFAULT_MODEL = "nomic-embed-text"

    def __init__(self, config: OllamaEmbeddingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(host=self.config.base_url)
        return self._client

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embed(model=self.model, input=texts)

        return response.get("embeddings", [])
