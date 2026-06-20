from rag.embedding.base import EmbeddingStrategy


class SentenceTransformerEmbeddingStrategy(EmbeddingStrategy):

    def __init__(
        self,
        model=None,
        model_name=None
    ):
        if isinstance(model, str):
            model_name = model
            model = None

        if model is None:
            if model_name is None:
                raise ValueError(
                    "SentenceTransformerEmbeddingStrategy requires either a "
                    "preloaded `model` object or a `model_name` to load."
                )
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(model_name)

        self.model = model

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        return self.model.encode(
            texts,
            normalize_embeddings=True
        )
