"""
Title/Passage parser implementation.

This module implements the ParsingStrategy for documents in the format:
    Title: <title text>
    Passage: <passage text>

This is the standard format used by RAGBench datasets.
"""

import re
from typing import Dict, Any, Optional
from .base import ParsingStrategy


class TitlePassageParser(ParsingStrategy):
    """
    Parser for documents with Title and Passage format.
    
    Expected format:
        Title: <title text>
        Passage: <passage text>
    
    This parser extracts the title and passage from raw documents
    and returns a canonical rag.models.Document object.
    
    Example:
        >>> parser = TitlePassageParser()
        >>> doc = parser.parse("Title: COVID-19\\nPassage: COVID-19 is a disease...")
        >>> print(doc.title)
        COVID-19
        >>> print(doc.content)
        COVID-19 is a disease...
    """

    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Parse a document with Title and Passage format.
        
        Args:
            raw_document: Raw document string with Title and Passage sections
            metadata: Optional metadata dictionary to attach to the document
            
        Returns:
            rag.models.Document: Canonical document with title, content, and metadata
            
        Raises:
            ValueError: If raw_document is None or empty
        """
        if not raw_document:
            raise ValueError("raw_document cannot be None or empty")

        # Import Document here to avoid circular imports
        from rag.models.document import Document

        # Extract title
        title_match = re.search(
            r"Title:\s*(.*?)\n",
            raw_document,
            re.DOTALL
        )

        # Extract passage
        passage_match = re.search(
            r"Passage:\s*(.*)",
            raw_document,
            re.DOTALL
        )

        title = (
            title_match.group(1).strip()
            if title_match else ""
        )

        content = (
            passage_match.group(1).strip()
            if passage_match else raw_document.strip()
        )

        # Merge provided metadata with extracted info
        final_metadata = metadata or {}
        final_metadata = {
            **final_metadata,
            'parser_type': 'title_passage'
        }

        return Document(
            title=title,
            content=content,
            metadata=final_metadata
        )
