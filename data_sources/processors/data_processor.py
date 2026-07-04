"""Data processor for datasets layer.

Orchestrates transformation from raw dataset samples to canonical Document objects.
"""

from typing import List, Dict, Any
from parsers.base import ParsingStrategy


class DataProcessor:
    """Process raw dataset into canonical Document objects.

    The processor accepts a parser strategy and uses it to transform
    raw documents into canonical Document objects.
    """

    def __init__(self, parser_strategy: ParsingStrategy):
        self.parser_strategy = parser_strategy

    def process_dataset(
        self,
        dataset: List[Dict[str, Any]]
    ) -> List:
        """Process dataset into canonical Document objects."""
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
        """Process a single sample into Document objects."""
        return self.process_dataset([sample])
