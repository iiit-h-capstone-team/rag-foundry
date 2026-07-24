"""Token-based chunking configuration.

Uses an actual tokenizer (tiktoken, HuggingFace, or SentencePiece) to
count and split by sub-word tokens rather than whitespace words.
"""

from dataclasses import dataclass
from enum import Enum

from rag.modules.chunking.config import BaseChunkingConfig


class TokenizerType(str, Enum):
    """Supported tokenizer backends."""
    TIKTOKEN = "tiktoken"
    HUGGINGFACE = "huggingface"
    SENTENCEPIECE = "sentencepiece"


@dataclass
class TokenChunkingConfig(BaseChunkingConfig):
    """Tunables for the token chunking strategy."""
    max_tokens: int = 200
    overlap_tokens: int = 20
    tokenizer_type: str = "tiktoken"
    encoding_name: str = "cl100k_base"
    model_name: str = ""
