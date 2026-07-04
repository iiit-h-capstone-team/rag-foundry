"""Parser module with registry-based strategy architecture."""

from parsers.base import ParsingStrategy
from parsers.registry import parser_registry, ParserRegistry
from parsers.enums import ParserType

from parsers.title_passage_parser import TitlePassageParser


__all__ = [
    "ParsingStrategy",
    "ParserRegistry",
    "parser_registry",
    "ParserType",
    "TitlePassageParser",
]
