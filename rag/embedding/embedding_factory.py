from rag.config.config import EmbeddingConfig
from rag.config.enums import EmbeddingType
from rag.embedding.sentence_transformer_embedding import SentenceTransformerEmbeddingStrategy
from rag.embedding.openai_embedding import OpenAIEmbeddingStrategy
from rag.embedding.ollama_embedding import OllamaEmbeddingStrategy
from rag.embedding.cohere_embedding import CohereEmbeddingStrategy
from rag.embedding.voyage_embedding import VoyageEmbeddingStrategy
from rag.embedding.huggingface_embedding import HuggingFaceEmbeddingStrategy
from rag.embedding.medcpt_embedding import MedCPTEmbeddingStrategy

class EmbeddingFactory:
    
    @staticmethod
    def create_embedder(
        config: EmbeddingConfig,
        **kwargs
    ):
        strategies = {
            EmbeddingType.SENTENCE_TRANSFORMER: lambda: SentenceTransformerEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.OPENAI: lambda: OpenAIEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.OLLAMA: lambda: OllamaEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.COHERE: lambda: CohereEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.VOYAGE: lambda: VoyageEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.HUGGINGFACE: lambda: HuggingFaceEmbeddingStrategy(
                config=config.config
            ),
            EmbeddingType.MEDCPT: lambda: MedCPTEmbeddingStrategy(
                config=config.config
            )
        }
        return strategies[config.type]()