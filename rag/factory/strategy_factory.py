from rag.config.config import (
    ChunkingConfig, 
    EmbeddingConfig, 
    RetrievalConfig, 
    GenerationConfig, 
    EvaluationConfig, 
    RerankerConfig, 
    VectorStoreConfig
)
from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
    RerankerType,
    VectorStoreType,
    GenerationType,
    EvaluationType,
    ProviderType
)

from rag.chunking.sentence_chunking import SentenceChunkingStrategy
from rag.chunking.fixed_window_chunking import FixedWindowChunkingStrategy
from rag.chunking.token_chunking import TokenChunkingStrategy

from rag.embedding.sentence_transformer_embedding import SentenceTransformerEmbeddingStrategy
from rag.embedding.openai_embedding import OpenAIEmbeddingStrategy

from rag.retrieval.dense_rerank import DenseRerankRetrievalStrategy
from rag.retrieval.dense_retrieval import DenseRetrievalStrategy
from rag.retrieval.hybrid_retrieval import HybridRetrievalStrategy

from rag.reranking.cross_encoder_reranker import CrossEncoderRerankerStrategy

from rag.generation.default_generation import DefaultGenerationStrategy

from rag.evaluation.trace_evaluation import TRACeEvaluationStrategy

from rag.vectorstores.faiss_store import FaissVectorStore


class StrategyFactory:

    @staticmethod
    def create_chunker(
        config: ChunkingConfig,
        **kwargs
    ):
        strategies = {
            ChunkingType.SENTENCE: lambda: SentenceChunkingStrategy(
                config=config
            ),
            ChunkingType.FIXED_WINDOW: lambda: FixedWindowChunkingStrategy(
                config=config
            ),
            ChunkingType.TOKEN: lambda: TokenChunkingStrategy(
                config=config
            )
        }
        return strategies[config.type]()

    @staticmethod
    def create_embedder(
        config: EmbeddingConfig,
        **kwargs
    ):
        strategies = {
            EmbeddingType.SENTENCE_TRANSFORMER: lambda: SentenceTransformerEmbeddingStrategy(
                config=config
            ),
            EmbeddingType.OPENAI: lambda: OpenAIEmbeddingStrategy(
                config=config
            )
        }
        return strategies[config.type]()

    @staticmethod
    def create_reranker(
        config: RerankerConfig,
        **kwargs
    ):
        strategies = {
            RerankerType.CROSS_ENCODER: lambda: CrossEncoderRerankerStrategy(
                config=config
            )
        }
        return strategies[config.type]()

    @staticmethod
    def create_vectorstore(
        config: VectorStoreConfig,
        **kwargs
    ):
        strategies = {
            VectorStoreType.FAISS: lambda: FaissVectorStore(
                config=config
            )
        }
        return strategies[config.type]()

    @staticmethod
    def create_retriever(
    config: RetrievalConfig,
        *,
        embedder,
        vector_store,
        reranker=None,
        bm25_store=None,
    ):
        strategies = {
            RetrievalType.DENSE_RERANK: lambda: DenseRerankRetrievalStrategy(
                config=config,
                embedder=embedder,
                vector_store=vector_store,
                reranker=reranker,
            ),
            RetrievalType.DENSE: lambda: DenseRetrievalStrategy(
                config=config,
                embedder=embedder,
                vector_store=vector_store,
                reranker=reranker,
            ),
            RetrievalType.HYBRID: lambda: HybridRetrievalStrategy(
                config=config,
                embedder=embedder,
                vector_store=vector_store,
                bm25_store=bm25_store,
            )
        }
        return strategies[config.type]()

    @staticmethod
    def create_generator(
        provider: ProviderType,
        config: GenerationConfig,
        **kwargs
    ):
        strategies = {
            GenerationType.DEFAULT: lambda: DefaultGenerationStrategy(
                provider=provider,
                config=config
            ),
        }
        return strategies[config.type]()

    @staticmethod
    def create_evaluator(
        provider: ProviderType,
        config: EvaluationConfig,
        **kwargs
    ):
        strategies = {
            EvaluationType.TRACE: lambda: TRACeEvaluationStrategy(
                provider=provider,
                config=config
            )
        }
        return strategies[config.type]()
