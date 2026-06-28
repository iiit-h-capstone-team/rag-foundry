from rag.config.config import GenerationConfig
from rag.config.enums import GenerationType
from rag.generation.default_generation import DefaultGenerationStrategy

class GeneratorFactory:
    
    @staticmethod
    def create_generator(
        config: GenerationConfig,
        *,
        provider,
    ):
        strategies = {
            GenerationType.DEFAULT: lambda: DefaultGenerationStrategy(
                config=config.config,
                provider=provider
            ),
        }
        return strategies[config.strategy]()