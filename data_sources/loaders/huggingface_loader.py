"""HuggingFace dataset loader implementation."""

from typing import List, Dict, Any, Optional
from datasets import load_dataset

from data_sources.loaders.base import DatasetLoader, DatasetLoadingConfig
from data_sources.loaders.registry import loader_registry
from data_sources.loaders.enums import LoaderType


@loader_registry.register(LoaderType.HUGGINGFACE)
class HuggingFaceLoader(DatasetLoader):
    """Loader for datasets from HuggingFace Hub."""

    def __init__(
        self,
        dataset_name: str,
        subset: Optional[str] = None,
        split: str = "train",
        config: DatasetLoadingConfig = None,
        hf_token: Optional[str] = None,
        **kwargs
    ):
        super().__init__(config)
        self.dataset_name = dataset_name
        self.subset = subset
        self.split = split
        self.hf_token = hf_token
        self.kwargs = kwargs

    def load(self) -> List[Dict[str, Any]]:
        """Load dataset from HuggingFace."""
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
        """Return information about the dataset."""
        data = self.load()
        info = super().info()
        info.update({
            'dataset_name': self.dataset_name,
            'subset': self.subset,
            'split': self.split,
            'source': 'huggingface'
        })
        return info
