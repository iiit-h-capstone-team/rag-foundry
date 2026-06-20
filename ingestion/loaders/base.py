"""
Base dataset loader for ingestion layer.

This module defines the abstract base class for dataset loaders.
Loaders are responsible for fetching raw data from various sources
(HuggingFace, local files, databases, APIs, etc.) and returning
them as a list of dictionaries.

Why separate loaders from parsers:
- Single Responsibility: Loaders fetch data, parsers transform it
- Open/Closed Principle: Easy to add new data sources without modifying existing code
- Dependency Inversion: Higher-level modules depend on abstractions
- Enables caching, batching, and other optimizations at the loader level
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DatasetLoadingConfig:
    """
    Configuration for dataset loading.
    
    Attributes:
        cache_dir: Optional directory to cache loaded data
        use_cache: Whether to use cached data if available
        limit: Optional limit on number of samples to load
    """
    cache_dir: Optional[str] = None
    use_cache: bool = True
    limit: Optional[int] = None


class DatasetLoader(ABC):
    """
    Abstract base class for dataset loaders.
    
    Each loader implementation knows how to fetch data from a specific
    source (e.g., HuggingFace, local files, databases, APIs). The loader
    returns raw data as a list of dictionaries, which is then processed
    by the DataProcessor and parsed by a ParsingStrategy.
    
    Example implementations:
    - RAGBenchLoader: Loads datasets from galileo-ai/ragbench on HuggingFace
    - LocalFileLoader: Loads data from local files (JSON, CSV, etc.)
    - DatabaseLoader: Loads data from SQL/NoSQL databases
    - APILoader: Loads data from REST APIs
    - ConfluenceLoader: Loads data from Confluence pages
    - SlackLoader: Loads data from Slack messages
    
    The flow is:
        Dataset Source
            ↓
        DatasetLoader.load()
            ↓
        Raw Samples (List[Dict])
            ↓
        DataProcessor.process_dataset()
            ↓
        Document (canonical)
    """

    def __init__(self, config: DatasetLoadingConfig = None):
        """
        Initialize the dataset loader.
        
        Args:
            config: DatasetLoadingConfig instance with loading options
        """
        self.config = config or DatasetLoadingConfig()
        self._data = None

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """
        Load and return data as list of dictionaries.
        
        Each dictionary represents a sample from the dataset with
        its raw fields (e.g., question, documents, response, etc.).
        
        Returns:
            List of dictionaries, where each dictionary is a dataset sample
            
        Raises:
            Exception: If loading fails for any reason
        """
        pass

    def load_sample(self, index: int = 0) -> Dict[str, Any]:
        """
        Load a single sample by index.
        
        Args:
            index: Index of the sample to load
            
        Returns:
            Dictionary representing the sample
            
        Raises:
            IndexError: If index is out of range
        """
        data = self.load()
        if index < len(data):
            return data[index]
        raise IndexError(
            f"Index {index} out of range for dataset with {len(data)} samples"
        )

    def load_batch(self, start: int = 0, end: int = None) -> List[Dict[str, Any]]:
        """
        Load a batch of samples.
        
        Args:
            start: Start index (inclusive)
            end: End index (exclusive), None means to the end
            
        Returns:
            List of dictionaries representing the batch
        """
        data = self.load()
        if end is None:
            end = len(data)
        return data[start:end]

    def info(self) -> Dict[str, Any]:
        """
        Return information about the dataset.
        
        Returns:
            Dictionary with dataset metadata including:
            - num_samples: Total number of samples
            - keys: Available fields in each sample
            - first_sample: The first sample for inspection
        """
        data = self.load()
        return {
            'num_samples': len(data),
            'keys': list(data[0].keys()) if data else [],
            'first_sample': data[0] if data else None
        }
