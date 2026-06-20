"""
Base parser strategy for document parsing.

This module defines the abstract base class for parsing strategies.
The strategy pattern allows for different parsing implementations (e.g., 
title/passage, markdown, JSON, PDF) without modifying the processor logic.

Why separate ingestion from rag:
- Ingestion handles dataset-specific formats and loading logic
- RAG layer operates only on canonical Document objects
- This separation follows the Single Responsibility Principle
- Makes the system extensible to new data sources (PDFs, Confluence, Slack, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ParsingStrategy(ABC):
    """
    Abstract base class for document parsing strategies.
    
    Each parsing strategy knows how to convert a raw document string
    into a canonical rag.models.Document object. This allows the
    ingestion layer to handle various data formats while the RAG
    layer remains format-agnostic.
    
    Example implementations:
    - TitlePassageParser: Parses "Title: ... Passage: ..." format
    - MarkdownParser: Parses markdown documents
    - JsonParser: Parses JSON documents
    - PdfParser: Parses PDF documents
    """

    @abstractmethod
    def parse(
        self,
        raw_document: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Parse a raw document into a canonical Document object.
        
        Args:
            raw_document: Raw document string in the strategy's expected format
            metadata: Optional metadata dictionary to attach to the document
            
        Returns:
            rag.models.Document: Canonical document object with title, content, and metadata
            
        Raises:
            ValueError: If the raw_document cannot be parsed
        """
        pass
