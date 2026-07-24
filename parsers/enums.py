"""Parser strategy types."""

from enum import Enum


class ParserType(str, Enum):
    """Available document parser strategies."""
    TITLE_PASSAGE = "title_passage"
    TITLE_PASSAGE_COMBINED = "title_passage_combined"
    NOOP = "noop"
