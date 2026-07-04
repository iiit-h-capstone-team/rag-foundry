"""HuggingFace embedding strategy implementation."""

import os

from embedding.base import EmbeddingStrategy
from embedding.registry import embedding_registry
from embedding.enums import EmbeddingType
from embedding.strategies.huggingface.config import HuggingFaceEmbeddingConfig


@embedding_registry.register(EmbeddingType.HUGGINGFACE)
class HuggingFaceEmbeddingStrategy(EmbeddingStrategy):
    """Embedding strategy using HuggingFace Inference API."""

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_API_URL = "https://api-inference.huggingface.co/models/"

    def __init__(self, config: HuggingFaceEmbeddingConfig):
        super().__init__(config)
        self._client = None

    @property
    def model(self) -> str:
        return self.config.model or self.config.model_name or self.DEFAULT_MODEL

    @property
    def api_url(self) -> str:
        if self.config.api_url:
            return self.config.api_url
        return f"{self.DEFAULT_API_URL}{self.model}"

    @property
    def client(self):
        if self._client is None:
            import requests
            self._client = requests.Session()
            api_key = os.environ.get("HUGGINGFACE_API_KEY")
            if api_key:
                self._client.headers.update({"Authorization": f"Bearer {api_key}"})
        return self._client

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.post(self.api_url, json={"inputs": texts})
        response.raise_for_status()

        result = response.json()
        if isinstance(result, list):
            return [item.get("embedding", []) for item in result]
        elif isinstance(result, dict):
            return result.get("embeddings", [])
        else:
            raise ValueError(f"Unexpected response format from HuggingFace API: {result}")
