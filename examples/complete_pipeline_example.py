"""
Complete RAG pipeline example using the configuration system.

The pipeline is a pure orchestrator (``rag.pipeline.rag_pipeline.RAGPipeline``):
it builds strategies from config and wires runtime dependencies. Providers are
created automatically from ``config.providers`` and resolve their credentials
from the environment variable each provider declares via ``api_key_env``.
"""

from rag.config.examples import get_config_by_name
from rag.config.loader import ConfigLoader  # noqa: F401  (handy for file configs)
from rag.models.document import Document  # noqa: F401  (used when building an index)
from rag.pipeline.rag_pipeline import RAGPipeline


# ============================================================
# USAGE EXAMPLES
# ============================================================

if __name__ == "__main__":

    # Example 1: Load a pre-built configuration
    print("Loading high quality configuration...")
    config = get_config_by_name('high_quality')

    # Example 2: Load from file
    # config = ConfigLoader.load('config/rag_config_high_quality.yaml')

    print("\nConfiguration loaded:")
    print(f"  Chunking:   {config.chunking.type.value}")
    print(f"  Embedding:  {config.embedding.type.value}")
    print(f"  Retrieval:  {config.retrieval.type.value}")
    print(
        f"  Generation: "
        f"{config.generation.provider} "
        f"({config.generation.config.model})"
    )
    print(
        f"  Evaluation: "
        f"{config.evaluation.type.value} "
        f"({config.evaluation.config.model})"
    )

    # Providers and strategies are initialized automatically from config:
    #
    # pipeline = RAGPipeline(config)
    #
    # documents = [
    #     Document(title="Doc 1", content="...", metadata={})
    # ]
    # pipeline.build_index(documents)
    #
    # result = pipeline.query("Your question here?")
    # pipeline.print_results(result)

    print("\nConfiguration system ready!")
