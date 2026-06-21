from rag.config.config import EmbeddingConfig
from rag.embedding.base import EmbeddingStrategy


class SentenceTransformerEmbeddingStrategy(EmbeddingStrategy):

    def __init__(
        self,
        config: EmbeddingConfig
    ):
        self.config = config

        model_name = self.config.model_name or self.config.model
        if not model_name:
            raise ValueError(
                "SentenceTransformerEmbeddingStrategy requires "
                "'model_name' (or 'model') in the embedding config."
            )

        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )
