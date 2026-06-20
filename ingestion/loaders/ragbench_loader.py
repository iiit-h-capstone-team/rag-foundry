"""
RAGBench dataset loader for ingestion layer.

This module implements the DatasetLoader for RAGBench datasets from HuggingFace.
RAGBench is a benchmark dataset for Retrieval-Augmented Generation systems,
containing various datasets like CovidQA, FEVEROUS, HotpotQA, etc.

This loader is responsible for fetching raw data from HuggingFace and
returning it as a list of dictionaries. The parsing and transformation
into canonical Document objects is handled by the DataProcessor and
ParsingStrategy.
"""

from typing import List, Dict, Any, Optional
from datasets import load_dataset
from .base import DatasetLoader, DatasetLoadingConfig


class RAGBenchLoader(DatasetLoader):
    """
    Load datasets from Galileo AI's RAGBench on HuggingFace.
    
    This loader fetches raw dataset samples from the galileo-ai/ragbench
    repository. Each sample contains fields like 'documents', 'question',
    'response', and various evaluation metrics.
    
    The loader returns raw data as-is, without any parsing. Parsing is
    handled by the DataProcessor using a ParsingStrategy.
    
    Example:
        >>> loader = RAGBenchLoader(
        ...     dataset_name="covidqa",
        ...     split="test",
        ...     config=DatasetLoadingConfig(limit=100)
        ... )
        >>> raw_data = loader.load()
        >>> print(len(raw_data))
        100
    """

    def __init__(
        self,
        dataset_name: str,
        split: str = "test",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize RAGBench data loader.

        Args:
            dataset_name: Name of dataset (e.g., "covidqa", "feverous", "hotpotqa")
            split: Dataset split (e.g., "test", "train", "validation")
            config: DatasetLoadingConfig instance
            hf_token: HuggingFace token for authentication (if needed)
        """
        super().__init__(config)
        self.dataset_name = dataset_name
        self.split = split
        self.hf_token = hf_token

    def load(self) -> List[Dict[str, Any]]:
        """
        Load RAGBench dataset from HuggingFace.

        Returns:
            List of dictionaries, where each dictionary is a dataset sample
            with fields like 'documents', 'question', 'response', etc.

        Raises:
            ValueError: If dataset loading fails
        """
        # Use cache if available
        if self._data is not None and self.config.use_cache:
            return self._data

        print(f"Loading RAGBench dataset: {self.dataset_name} ({self.split})...")

        try:
            dataset = load_dataset(
                "galileo-ai/ragbench",
                name=self.dataset_name,
                split=self.split,
                token=self.hf_token
            )
        except Exception as e:
            raise ValueError(
                f"Failed to load dataset {self.dataset_name} "
                f"from RAGBench: {str(e)}"
            )

        # Convert to list of dictionaries
        data = [dict(sample) for sample in dataset]

        # Apply limit if specified
        if self.config.limit:
            data = data[:self.config.limit]

        print(f"Loaded {len(data)} samples")

        # Cache if enabled
        if self.config.use_cache:
            self._data = data

        return data

    def info(self) -> Dict[str, Any]:
        """
        Return information about the dataset.

        Returns:
            Dictionary with dataset metadata including source, dataset_name,
            split, num_samples, keys, and first_sample
        """
        data = self.load()
        info = super().info()
        info.update({
            'dataset_name': self.dataset_name,
            'split': self.split,
            'source': 'galileo-ai/ragbench'
        })
        return info


class RAGBenchCovidQALoader(RAGBenchLoader):
    """
    Specific loader for CovidQA dataset.

    This is a convenience class for loading the CovidQA dataset
    from RAGBench without needing to specify the dataset_name.
    """

    def __init__(
        self,
        split: str = "test",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize CovidQA loader.

        Args:
            split: Dataset split (e.g., "test", "train", "validation")
            config: DatasetLoadingConfig instance
            hf_token: HuggingFace token for authentication
        """
        super().__init__(
            dataset_name="covidqa",
            split=split,
            config=config,
            hf_token=hf_token
        )


class RAGBenchFeverousLoader(RAGBenchLoader):
    """
    Specific loader for FEVEROUS dataset.

    This is a convenience class for loading the FEVEROUS dataset
    from RAGBench without needing to specify the dataset_name.
    """

    def __init__(
        self,
        split: str = "test",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize FEVEROUS loader.

        Args:
            split: Dataset split (e.g., "test", "train", "validation")
            config: DatasetLoadingConfig instance
            hf_token: HuggingFace token for authentication
        """
        super().__init__(
            dataset_name="feverous",
            split=split,
            config=config,
            hf_token=hf_token
        )


class RAGBenchHotpotQALoader(RAGBenchLoader):
    """
    Specific loader for HotpotQA dataset.

    This is a convenience class for loading the HotpotQA dataset
    from RAGBench without needing to specify the dataset_name.
    """

    def __init__(
        self,
        split: str = "test",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None
    ):
        """
        Initialize HotpotQA loader.

        Args:
            split: Dataset split (e.g., "test", "train", "validation")
            config: DatasetLoadingConfig instance
            hf_token: HuggingFace token for authentication
        """
        super().__init__(
            dataset_name="hotpotqa",
            split=split,
            config=config,
            hf_token=hf_token
        )
