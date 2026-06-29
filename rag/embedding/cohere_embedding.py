import os
from rag.config.config import CohereEmbeddingConfig
from rag.embedding.base import EmbeddingStrategy


class CohereEmbeddingStrategy(EmbeddingStrategy):

    DEFAULT_MODEL = "embed-english-v3"

    def __init__(
        self,
        config: CohereEmbeddingConfig
    ):
        self.config = config
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
            texts=texts,
            model=self.model,
            input_type=self.config.input_type
        )

        return response.embeddings
