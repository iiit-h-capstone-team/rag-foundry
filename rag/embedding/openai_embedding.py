from rag.embedding.base import EmbeddingStrategy


class OpenAIEmbeddingStrategy(EmbeddingStrategy):

    def __init__(
        self,
        client,
        model: str = "text-embedding-3-small"
    ):
        self.client = client
        self.model = model

    def embed(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        response = self.client.embeddings.create(
            input=texts,
            model=self.model
        )

        embeddings = [item.embedding for item in response.data]
        return embeddings
