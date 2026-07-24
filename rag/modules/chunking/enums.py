"""Chunking strategy type enumerations."""

from enum import Enum


class ChunkingType(str, Enum):
    """Available chunking strategies."""
    SENTENCE = "sentence"
    FIXED_WINDOW = "fixed_window"
    FIXED_WORD = "fixed_word"
    TOKEN = "token"
    SEMANTIC = "semantic"
