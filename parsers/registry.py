"""Parser strategy registry."""

from core.registry import BaseRegistry
from parsers.base import ParsingStrategy


class ParserRegistry(BaseRegistry[ParsingStrategy]):
    """Registry for document parser strategy plugins."""
    pass


parser_registry = ParserRegistry()
