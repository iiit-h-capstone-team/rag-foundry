"""
Generic HuggingFace dataset loader for ingestion layer.

This module implements a generic DatasetLoader for any dataset on HuggingFace.
It provides a flexible interface to load datasets directly by specifying the
dataset name, with optional parameters for split, subset, and authentication.

The loader returns raw data as-is, without any parsing. Parsing and
transformation into canonical Document objects is handled by the DataProcessor
and ParsingStrategy.
"""

from typing import List, Dict, Any, Optional
from datasets import load_dataset
from .base import DatasetLoader, DatasetLoadingConfig


class HuggingFaceLoader(DatasetLoader):
    """
    Generic loader for datasets from HuggingFace Hub.

    This loader fetches raw dataset samples from any HuggingFace dataset
    repository. It provides a flexible interface to load datasets by name,
    with support for dataset subsets, splits, and authentication.

    The loader returns raw data as-is, without any parsing. Parsing is
    handled by the DataProcessor using a ParsingStrategy.

    Example:
        >>> loader = HuggingFaceLoader(
        ...     dataset_name="imdb",
        ...     split="test",
        ...     config=DatasetLoadingConfig(limit=100)
        ... )
        >>> raw_data = loader.load()
        >>> print(len(raw_data))
        100

        >>> # Load a dataset with a specific subset/config
        >>> loader = HuggingFaceLoader(
        ...     dataset_name="glue",
        ...     subset="mrpc",
        ...     split="validation"
        ... )
        >>> raw_data = loader.load()
    """

    def __init__(
        self,
        dataset_name: str,
        subset: Optional[str] = None,
        split: str = "train",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize HuggingFace data loader.

        Args:
            dataset_name: Name of the dataset on HuggingFace Hub (e.g., "imdb", "glue")
            subset: Optional dataset subset/config name (e.g., "mrpc" for glue)
            split: Dataset split (e.g., "train", "test", "validation")
            config: DatasetLoadingConfig instance
            hf_token: HuggingFace token for authentication (if needed)
            **kwargs: Additional arguments to pass to load_dataset
        """
        super().__init__(config)
        self.dataset_name = dataset_name
        self.subset = subset
        self.split = split
        self.hf_token = hf_token
        self.kwargs = kwargs

    def load(self) -> List[Dict[str, Any]]:
        """
        Load dataset from HuggingFace.

        Returns:
            List of dictionaries, where each dictionary is a dataset sample
            with fields specific to the dataset.

        Raises:
            ValueError: If dataset loading fails
        """
        # Use cache if available
        if self._data is not None and self.config.use_cache:
            return self._data

        subset_str = f"/{self.subset}" if self.subset else ""
        print(f"Loading HuggingFace dataset: {self.dataset_name}{subset_str} ({self.split})...")

        try:
            load_args = {
                "path": self.dataset_name,
                "split": self.split,
                "token": self.hf_token,
            }
            
            if self.subset:
                load_args["name"] = self.subset
            
            load_args.update(self.kwargs)
            
            dataset = load_dataset(**load_args)
        except Exception as e:
            raise ValueError(
                f"Failed to load dataset {self.dataset_name} "
                f"(subset: {self.subset}, split: {self.split}): {str(e)}"
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
            subset, split, num_samples, keys, and first_sample
        """
        data = self.load()
        info = super().info()
        info.update({
            'dataset_name': self.dataset_name,
            'subset': self.subset,
            'split': self.split,
            'source': 'huggingface'
        })
        return info
