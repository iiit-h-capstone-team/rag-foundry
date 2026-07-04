"""Base dataset loader strategy class."""

from abc import abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from core.strategy import BaseStrategy


@dataclass
class DatasetLoadingConfig:
    """Configuration for dataset loading."""
    cache_dir: Optional[str] = None
    use_cache: bool = True
    limit: Optional[int] = None


class DatasetLoader(BaseStrategy):
    """Base class for dataset loader strategies.

    Each loader implementation knows how to fetch data from a specific
    source (e.g., HuggingFace, local files, databases, APIs). The loader
    returns raw data as a list of dictionaries.
    """

    def __init__(self, config: DatasetLoadingConfig = None):
        super().__init__(config)
        self.config = config or DatasetLoadingConfig()
        self._data = None

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """Load and return data as list of dictionaries."""
        pass

    def load_sample(self, index: int = 0) -> Dict[str, Any]:
        """Load a single sample by index."""
        data = self.load()
        if index < len(data):
            return data[index]
        raise IndexError(
            f"Index {index} out of range for dataset with {len(data)} samples"
        )

    def load_batch(self, start: int = 0, end: int = None) -> List[Dict[str, Any]]:
        """Load a batch of samples."""
        data = self.load()
        if end is None:
            end = len(data)
        return data[start:end]

    def info(self) -> Dict[str, Any]:
        """Return information about the dataset."""
        data = self.load()
        return {
            'num_samples': len(data),
            'keys': list(data[0].keys()) if data else [],
            'first_sample': data[0] if data else None
        }
