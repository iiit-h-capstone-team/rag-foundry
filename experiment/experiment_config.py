from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    config_dir: Path
    report_dir: Path
    cache_dir: Path | None = None

    num_queries: int = 246
    parallel: bool = False
    max_workers: int = 4
    
    # Data loading configuration
    data_loader: dict | None = None  # {type: "huggingface", config: {...}}
    data_parser: str | None = None  # Parser type (e.g., "title_passage")
    
    # Report configuration
    report_strategy: str = "detailed_query"  # Report strategy to use

    @classmethod
    def load(cls, path: str | Path):
        path = Path(path)

        with path.open("r") as f:
            data = yaml.safe_load(f)

        return cls(
            config_dir=Path(data["config_dir"]),
            report_dir=Path(data["report_dir"]),
            cache_dir=Path(data.get("cache_dir")) if data.get("cache_dir") else None,
            num_queries=data.get("num_queries", 246),
            parallel=data.get("parallel", False),
            max_workers=data.get("max_workers", 4),
            data_loader=data.get("data_loader"),
            data_parser=data.get("data_parser"),
            report_strategy=data.get("report_strategy", "detailed_query"),
        )