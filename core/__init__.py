"""Core plugin architecture for RAG Foundry."""

from core.strategy import BaseStrategy
from core.registry import BaseRegistry
from core.config import coerce_config

__all__ = [
    "BaseStrategy",
    "BaseRegistry",
    "coerce_config",
]
