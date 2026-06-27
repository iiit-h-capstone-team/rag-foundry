from rag.config.config import SentenceTransformerEmbeddingConfig
from rag.embedding.base import EmbeddingStrategy
from rag.runtime.model_cache import get_sentence_transformer


class SentenceTransformerEmbeddingStrategy(EmbeddingStrategy):

    def __init__(
        self,
        config: SentenceTransformerEmbeddingConfig
    ):
        self.config = config

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

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )
