"""
Data processor for ingestion layer.

This module implements the data processor that orchestrates the transformation
from raw dataset samples to canonical Document objects.

The processor:
1. Iterates over dataset samples
2. Extracts raw documents from each sample
3. Creates metadata for each document
4. Uses a parser strategy to parse raw documents into canonical Documents
5. Returns a list of canonical Document objects

Why separate processing from parsing:
- Single Responsibility: Processor orchestrates, parser transforms
- Strategy Pattern: Processor can use any parser without modification
- Open/Closed Principle: Easy to add new parsers without changing processor
- Dependency Inversion: Processor depends on ParsingStrategy abstraction
"""

from typing import List, Dict, Any
from ..parsers.base import ParsingStrategy


class DataProcessor:
    """
    Process raw dataset into canonical Document objects.
    
    The processor accepts a parser strategy and uses it to transform
    raw documents into canonical rag.models.Document objects.
    
    The processor contains no parsing logic - it only orchestrates
    the flow from raw samples to parsed documents.
    
    Example:
        >>> from ingestion import HuggingFaceLoader
        >>> from ingestion.parsers.strategy_factory import ParserFactory, ParserType
        >>> from ingestion.processors.data_processor import DataProcessor
        >>> 
        >>> # Load raw data
        >>> loader = HuggingFaceLoader(
        ...     dataset_name="galileo-ai/ragbench",
        ...     subset="covidqa",
        ...     split="test"
        ... )
        >>> raw_data = loader.load()
        >>> 
        >>> # Create parser strategy
        >>> parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)
        >>> 
        >>> # Process data
        >>> processor = DataProcessor(parser_strategy=parser)
        >>> documents = processor.process_dataset(raw_data)
        >>> 
        >>> print(f"Processed {len(documents)} documents")
    """

    def __init__(self, parser_strategy: ParsingStrategy):
        """
        Initialize the data processor with a parser strategy.
        
        Args:
            parser_strategy: An instance of a ParsingStrategy implementation
                           (e.g., TitlePassageParser, MarkdownParser, etc.)
        """
        self.parser_strategy = parser_strategy

    def process_dataset(
        self,
        dataset: List[Dict[str, Any]]
    ) -> List:
        """
        Process dataset into canonical Document objects.
        
        This method iterates over the dataset samples, extracts raw documents,
        creates metadata, and uses the parser strategy to transform each
        raw document into a canonical Document object.
        
        Args:
            dataset: List of dataset samples (dictionaries with 'documents' field)
            
        Returns:
            List of rag.models.Document objects
            
        Note:
            Chunking should be done using rag.chunking strategies via StrategyFactory.
            This processor only handles parsing, not chunking.
        """
        documents = []

        for sample_idx, sample in enumerate(dataset):
            # Extract raw documents from the sample
            raw_docs = [
                doc.strip()
                for doc in sample.get("documents", [])
                if doc and doc.strip()
            ]

            # Process each raw document
            for doc_idx, raw_doc in enumerate(raw_docs):
                # Create metadata
                metadata = {
                    "doc_id": f"sample_{sample_idx}_doc_{doc_idx}",
                    "sample_index": sample_idx,
                    "source": "ragbench"
                }

                # Use parser strategy to parse the raw document
                document = self.parser_strategy.parse(raw_doc, metadata)
                documents.append(document)

        return documents

    def process_sample(
        self,
        sample: Dict[str, Any]
    ) -> List:
        """
        Process a single sample into Document objects.
        
        Args:
            sample: A single dataset sample (dictionary with 'documents' field)
            
        Returns:
            List of rag.models.Document objects
        """
        return self.process_dataset([sample])
