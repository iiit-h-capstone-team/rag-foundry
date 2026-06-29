from rag.config.config import OllamaEmbeddingConfig
from rag.embedding.base import EmbeddingStrategy


class OllamaEmbeddingStrategy(EmbeddingStrategy):

    DEFAULT_MODEL = "nomic-embed-text"

    def __init__(
        self,
        config: OllamaEmbeddingConfig
    ):
        self.config = config
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

        response = self.client.embed(
            model=self.model,
            input=texts
        )

        return response.get('embeddings', [])
