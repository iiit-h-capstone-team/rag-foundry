class RAGPipeline:
    """Complete RAG pipeline using configuration."""

    def __init__(self, config: RAGConfig):
        """
        Initialize RAG pipeline from configuration.

        Args:
            config: RAGConfig instance
        """
        self.config = config

        # Create strategies from config
        self._initialize_providers()
        self._initialize_strategies()

    def _initialize_providers(self):
        """
        Create all providers declared in config.
        Reuses existing instances through ProviderManager.
        """

        for provider_name, provider_config in (
            self.config.providers.items()
        ):

            ProviderManager.register(
                provider_name=provider_name,
                provider_type=provider_config.type,
                config=provider_config
            )

    def _initialize_strategies(self):
        """Initialize all strategies from config."""

        # Chunking
        self.chunker = StrategyFactory.create_chunker(
            self.config.chunking
        )

        # Embedding
        self.embedder = StrategyFactory.create_embedder(
            self.config.embedding
        )

        # Vector Store
        self.vector_store = StrategyFactory.create_vectorstore(
            self.config.vector_store.type,
            embedding_config=self.config.embedding
        )

        # Reranking (only used by rerank-based retrievers). Build from config;
        # a prebuilt reranker/model passed via clients takes precedence.
        self.reranker = (
        StrategyFactory.create_reranker(
            self.config.reranker
        )
        if self.config.reranker
        else None
        )


        # Retrieval
        self.retriever = StrategyFactory.create_retriever(
            config=self.config.retrieval,
            embedder=self.embedder,
            vector_store=self.vector_store,
            reranker=self.reranker
        )

        # Generation
        
        generation_provider = (
            ProviderManager.get_provider(
                self.config.generation.provider
            )
        )

        self.generator = StrategyFactory.create_generator(
            config=self.config.generation,
            provider=generation_provider
        )

        # Evaluation
        evaluation_provider = (
            ProviderManager.get_provider(
                self.config.evaluation.provider
            )
        )
        self.evaluator = StrategyFactory.create_evaluator(
            config=self.config.evaluation,
            provider=evaluation_provider
        )

    def build_index(self, documents: list[Document]):
        """Build vector index from documents."""
        print(f"Processing {len(documents)} documents...")

        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)

        print(f"Created {len(all_chunks)} chunks")

        # Generate embeddings
        texts = [chunk.text for chunk in all_chunks]
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.embedder.embed(texts)
        embeddings = np.array(embeddings).astype('float32')

        # Add to vector store
        self.vector_store.add(embeddings, all_chunks)
        print(f"Vector store ready with {len(all_chunks)} chunks")

    def query(self, query: str, top_k: int = None) -> dict:
        """Run complete RAG query."""
        if top_k is None:
            top_k = self.config.retrieval.top_k

        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)

        # 1. Retrieve
        print("\n[1] Retrieving documents...")
        retrieved = self.retriever.retrieve(query, top_k=top_k)
        print(f"Retrieved {len(retrieved)} documents")

        # Format for generation
        retrieved_docs = [
            {
                "text": r["chunk"].text,
                "metadata": r["chunk"].metadata
            }
            for r in retrieved
        ]

        # 2. Generate
        print("\n[2] Generating response...")
        context = "\n\n".join([
            f"[Document {i+1}]\n{doc['text']}"
            for i, doc in enumerate(retrieved_docs)
        ])

        response = self.generator.generate(
            config={
                "query": query,
                "context": context,
                "max_tokens": self.config.generation.max_tokens,
                "temperature": self.config.generation.temperature
            }
        )
        print(f"Response generated ({len(response)} chars)")

        # 3. Evaluate
        print("\n[3] Evaluating response...")
        scores = self.evaluator.evaluate(
            config={
                "query": query,
                "retrieved_docs": retrieved_docs,
                "response": response
            }
        )
        print(f"Evaluation complete")

        return {
            'query': query,
            'retrieved_docs': retrieved_docs,
            'response': response,
            'scores': scores
        }

    def print_results(self, result: dict):
        """Pretty print query results."""
        print(f"\n{'='*60}")
        print("QUERY RESULTS")
        print('='*60)

        print(f"\nQuery: {result['query']}")

        print(f"\n--- Retrieved Documents ({len(result['retrieved_docs'])}) ---")
        for i, doc in enumerate(result['retrieved_docs'][:3], 1):
            print(f"\n{i}. {doc['text'][:200]}...")

        print(f"\n--- Generated Response ---")
        print(result['response'][:500] + "..." if len(result['response']) > 500 else result['response'])

        print(f"\n--- TRACe Scores ---")
        scores = result['scores']
        print(f"  Relevance:    {scores['relevance_score']:.4f}")
        print(f"  Utilization:  {scores['utilization_score']:.4f}")
        print(f"  Completeness: {scores['completeness_score']:.4f}")
        print(f"  Adherence:    {scores['adherence_score']}")

        print(f"\n{'='*60}\n")
