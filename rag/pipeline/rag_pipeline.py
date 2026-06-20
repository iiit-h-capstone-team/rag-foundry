class RAGPipeline:
    def __init__(
        self,
        chunker,
        embedder,
        retriever
    ):

        self.chunker = chunker

        self.embedder = embedder

        self.retriever = retriever

    def describe(self):

        print(
            f"""
    Chunker:
    {self.chunker.__class__.__name__}

    Embedder:
    {self.embedder.__class__.__name__}

    Retriever:
    {self.retriever.__class__.__name__}
    """
        )