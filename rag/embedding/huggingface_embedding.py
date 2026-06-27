import os
from rag.config.config import HuggingFaceEmbeddingConfig
from rag.embedding.base import EmbeddingStrategy


class HuggingFaceEmbeddingStrategy(EmbeddingStrategy):

    DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_API_URL = "https://api-inference.huggingface.co/models/"

    def __init__(
        self,
        config: HuggingFaceEmbeddingConfig
    ):
        self.config = config
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

        response = self.client.post(
            self.api_url,
            json={"inputs": texts}
        )
        response.raise_for_status()

        result = response.json()
        if isinstance(result, list):
            return [item.get("embedding", []) for item in result]
        elif isinstance(result, dict):
            return result.get("embeddings", [])
        else:
            raise ValueError(f"Unexpected response format from HuggingFace API: {result}")
