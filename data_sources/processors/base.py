"""Base processing step class."""

from abc import abstractmethod
from typing import List

from core.strategy import BaseStrategy
from rag.models.document import Document


class ProcessingStep(BaseStrategy):
    """Base class for data processing steps.

    Each step transforms a list of Documents into a (possibly filtered
    or augmented) list of Documents. Steps are composed into a pipeline
    that runs them in sequence.
    """

    @abstractmethod
    def process(self, documents: List[Document]) -> List[Document]:
        """Process a list of documents.

        Args:
            documents: Input document list.

        Returns:
            Transformed document list.
        """
        pass
