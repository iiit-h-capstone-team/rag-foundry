"""MedCPT embedding configuration."""

from dataclasses import dataclass

from embedding.config import BaseEmbeddingConfig


@dataclass
class MedCPTEmbeddingConfig(BaseEmbeddingConfig):
    """Tunables for the MedCPT embedding strategy (dual encoder)."""
    query_model_name: str = "ncbi/MedCPT-Query-Encoder"
    article_model_name: str = "ncbi/MedCPT-Article-Encoder"
    dimension: int = 768
