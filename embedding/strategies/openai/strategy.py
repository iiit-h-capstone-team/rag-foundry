"""OpenAI embedding strategy implementation."""

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.openai.config import OpenAIEmbeddingConfig


@embedding_registry.register(EmbeddingType.OPENAI)
class OpenAIEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using OpenAI API."""

    DEFAULT_MODEL = "text-embedding-3-small"

    def __init__(self, config: OpenAIEmbeddingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI()
        return self._client

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(input=texts, model=self.model)

        return [item.embedding for item in response.data]
