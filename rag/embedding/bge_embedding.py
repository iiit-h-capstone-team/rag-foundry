from rag.embedding.base import (
    EmbeddingStrategy
)

class BGEEmbeddingStrategy(
    EmbeddingStrategy
):

    def __init__(
        self,
        model
    ):
        self.model = model

    def embed(
        self,
        texts
    ):

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )