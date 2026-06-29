from rag.config.config import ChunkingConfig
from rag.config.enums import ChunkingType
from rag.chunking.sentence_chunking import SentenceChunkingStrategy
from rag.chunking.fixed_window_chunking import FixedWindowChunkingStrategy
from rag.chunking.token_chunking import TokenChunkingStrategy
from rag.chunking.semantic_chunking import SemanticChunkingStrategy

class ChunkingFactory:
    
    @staticmethod
    def create_chunker(
        config: ChunkingConfig,
        **kwargs
    ):
        strategies = {
            ChunkingType.SENTENCE: lambda: SentenceChunkingStrategy(
                config=config.config
            ),
            ChunkingType.FIXED_WINDOW: lambda: FixedWindowChunkingStrategy(
                config=config.config
            ),
            ChunkingType.TOKEN: lambda: TokenChunkingStrategy(
                config=config.config
            ),
            ChunkingType.SEMANTIC: lambda: SemanticChunkingStrategy(
                config=config.config
            )
        }
        return strategies[config.type]()
