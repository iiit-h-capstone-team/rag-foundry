"""
Parser factory for creating parsing strategies.

This module implements the Factory pattern for creating parser instances.
The factory allows for easy extension with new parser types without
modifying the processor logic.

Why use the strategy pattern:
- Open/Closed Principle: Open for extension, closed for modification
- Single Responsibility: Each parser handles one format
- Dependency Inversion: Processor depends on abstraction (ParsingStrategy)
- Easy to add new parsers (Markdown, JSON, PDF, etc.) without changing existing code
"""

from enum import Enum
from typing import Dict, Type
from .base import ParsingStrategy
from .title_passage_parser import TitlePassageParser


class ParserType(str, Enum):
    """
    Enumeration of available parser types.
    
    Each enum value corresponds to a specific parsing strategy implementation.
    New parser types can be added here without modifying existing code.
    
    Available parsers:
    - TITLE_PASSAGE: Parses "Title: ... Passage: ..." format (RAGBench standard)
    
    Future parsers (to be added):
    - MARKDOWN: Parses markdown documents
    - JSON: Parses JSON documents
    - PDF: Parses PDF documents
    - CONFLUENCE: Parses Confluence pages
    - SLACK: Parses Slack messages
    """
    TITLE_PASSAGE = "title_passage"
    # Future parsers can be added here:
    # MARKDOWN = "markdown"
    # JSON = "json"
    # PDF = "pdf"
    # CONFLUENCE = "confluence"
    # SLACK = "slack"


class ParserFactory:
    """
    Factory for creating parser instances.
    
    This factory implements the Factory pattern to create parser instances
    based on the ParserType enum. It maintains a registry of available parsers
    and allows for easy extension with new parser types.
    
    Example:
        >>> parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)
        >>> document = parser.parse("Title: COVID-19\\nPassage: ...")
    """

    # Registry of available parsers
    _PARSERS: Dict[ParserType, Type[ParsingStrategy]] = {
        ParserType.TITLE_PASSAGE: TitlePassageParser,
    }

    @classmethod
    def create_parser(cls, parser_type: ParserType) -> ParsingStrategy:
        """
        Create a parser instance based on the specified type.
        
        Args:
            parser_type: The type of parser to create (from ParserType enum)
            
        Returns:
            ParsingStrategy: An instance of the requested parser
            
        Raises:
            ValueError: If the parser_type is not registered
        """
        parser_class = cls._PARSERS.get(parser_type)
        
        if parser_class is None:
            available = [pt.value for pt in cls._PARSERS.keys()]
            raise ValueError(
                f"Unknown parser type: {parser_type}. "
                f"Available parsers: {available}"
            )
        
        return parser_class()

    @classmethod
    def register_parser(
        cls,
        parser_type: ParserType,
        parser_class: Type[ParsingStrategy]
    ):
        """
        Register a new parser type.
        
        This method allows for dynamic registration of new parsers at runtime,
        enabling extension without modifying the factory code.
        
        Args:
            parser_type: The enum value for the parser type
            parser_class: The parser class to register
            
        Example:
            >>> class MarkdownParser(ParsingStrategy):
            ...     def parse(self, raw_document, metadata=None):
            ...         # Implementation
            ...         pass
            >>> ParserFactory.register_parser(
            ...     ParserType.MARKDOWN, MarkdownParser
            ... )
        """
        cls._PARSERS[parser_type] = parser_class

    @classmethod
    def available_parsers(cls) -> list[str]:
        """
        Get list of available parser types.
        
        Returns:
            List of string values representing available parser types
        """
        return [pt.value for pt in cls._PARSERS.keys()]
