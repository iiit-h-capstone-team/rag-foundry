from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ExperimentConfig:
    config_dir: Path
    report_dir: Path
    cache_dir: Path | None = None

    # Query range configuration
    start_index: int = 0
    end_index: int | None = None
    
    # Parallel execution configuration
    parallel: bool = False
    max_workers: int = 4
    
    # Temporary directory for JSONL files
    temp_dir: Path = Path("./temp")
    
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

        # Handle backward compatibility: convert num_queries to end_index
        if "num_queries" in data and "end_index" not in data:
            data["end_index"] = data["num_queries"]

        return cls(
            config_dir=Path(data["config_dir"]),
            report_dir=Path(data["report_dir"]),
            cache_dir=Path(data.get("cache_dir")) if data.get("cache_dir") else None,
            start_index=data.get("start_index", 0),
            end_index=data.get("end_index"),
            parallel=data.get("parallel", False),
            max_workers=data.get("max_workers", 4),
            temp_dir=Path(data.get("temp_dir", "./temp")),
            data_loader=data.get("data_loader"),
            data_parser=data.get("data_parser"),
            report_strategy=data.get("report_strategy", "detailed_query"),
        )