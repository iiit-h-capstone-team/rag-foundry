from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
    RerankerType,
    VectorStoreType,
    GenerationType,
    EvaluationType
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

from rag.generation.groq_generation import GroqGenerationStrategy
from rag.generation.openai_generation import OpenAIGenerationStrategy

from rag.evaluation.trace_evaluation import TRACeEvaluationStrategy

from rag.vectorstores.faiss_store import FaissVectorStore


class StrategyFactory:

    @staticmethod
    def create_chunker(
        chunking_type,
        **kwargs
    ):
        strategies = {
            ChunkingType.SENTENCE: lambda: SentenceChunkingStrategy(
                max_words=kwargs.get('max_words', 100),
                overlap_sentences=kwargs.get('overlap_sentences', 1)
            ),
            ChunkingType.FIXED_WINDOW: lambda: FixedWindowChunkingStrategy(
                window_size=kwargs.get('window_size', 256),
                overlap=kwargs.get('overlap', 50)
            ),
            ChunkingType.TOKEN: lambda: TokenChunkingStrategy(
                max_tokens=kwargs.get('max_tokens', 200),
                overlap_tokens=kwargs.get('overlap_tokens', 20)
            )
        }
        return strategies[chunking_type]()

    @staticmethod
    def create_embedder(
        embedding_type,
        **kwargs
    ):
        strategies = {
            EmbeddingType.SENTENCE_TRANSFORMER: lambda: SentenceTransformerEmbeddingStrategy(
                model=kwargs.get('model'),
                model_name=kwargs.get('model_name')
            ),
            EmbeddingType.OPENAI: lambda: OpenAIEmbeddingStrategy(
                client=kwargs.get('client'),
                model=kwargs.get('model', 'text-embedding-3-small')
            )
        }
        return strategies[embedding_type]()

    @staticmethod
    def create_reranker(
        reranker_type,
        **kwargs
    ):
        strategies = {
            RerankerType.CROSS_ENCODER: lambda: CrossEncoderRerankerStrategy(
                model=kwargs.get('model'),
                model_name=kwargs.get('model_name')
            )
        }
        return strategies[reranker_type]()

    @staticmethod
    def create_vectorstore(
        vectorstore_type,
        **kwargs
    ):
        strategies = {
            VectorStoreType.FAISS: lambda: FaissVectorStore(
                dimension=kwargs.get('dimension')
            )
        }
        return strategies[vectorstore_type]()

    @staticmethod
    def create_retriever(
        retriever_type,
        **kwargs
    ):
        strategies = {
            RetrievalType.DENSE_RERANK: lambda: DenseRerankRetrievalStrategy(
                embedder=kwargs.get('embedder'),
                vector_store=kwargs.get('vector_store'),
                reranker=kwargs.get('reranker'),
                initial_k=kwargs.get('initial_k', 20)
            ),
            RetrievalType.DENSE: lambda: DenseRetrievalStrategy(
                embedder=kwargs.get('embedder'),
                vector_store=kwargs.get('vector_store')
            ),
            RetrievalType.HYBRID: lambda: HybridRetrievalStrategy(
                embedder=kwargs.get('embedder'),
                vector_store=kwargs.get('vector_store'),
                bm25_store=kwargs.get('bm25_store'),
                dense_weight=kwargs.get('dense_weight', 0.7),
                sparse_weight=kwargs.get('sparse_weight', 0.3)
            )
        }
        return strategies[retriever_type]()

    @staticmethod
    def create_generator(
        generation_type,
        **kwargs
    ):
        strategies = {
            GenerationType.GROQ: lambda: GroqGenerationStrategy(
                client=kwargs.get('client'),
                model=kwargs.get('model', 'llama-3.1-8b-instant')
            ),
            GenerationType.OPENAI: lambda: OpenAIGenerationStrategy(
                client=kwargs.get('client'),
                model=kwargs.get('model', 'gpt-4')
            )
        }
        return strategies[generation_type]()

    @staticmethod
    def create_evaluator(
        evaluation_type,
        **kwargs
    ):
        strategies = {
            EvaluationType.TRACE: lambda: TRACeEvaluationStrategy(
                judge_client=kwargs.get('judge_client'),
                model=kwargs.get('model', 'llama-3.3-70b-versatile')
            )
        }
        return strategies[evaluation_type]()
