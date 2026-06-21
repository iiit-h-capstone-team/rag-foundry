from rag.config.config import OpenAIEmbeddingConfig
from rag.embedding.base import EmbeddingStrategy


class OpenAIEmbeddingStrategy(EmbeddingStrategy):

    DEFAULT_MODEL = "text-embedding-3-small"

    def __init__(
        self,
        config: OpenAIEmbeddingConfig
    ):
        self.config = config
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

        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )

        return [item.embedding for item in response.data]
