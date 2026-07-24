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
    query_workers: int = 4  # intra-config query parallelism
    
    # Retry configuration
    max_retry_rounds: int = 3
    retry_delay_seconds: int = 60
    
    # Temporary directory for JSONL files (partial runs, query results)
    temp_dir: Path = Path("./temp")
    
    # Cache configuration (applied to all RAG configs unless overridden)
    cache: dict | None = None  # {enabled: bool, cache_dir: str}
    
    # Data loading configuration
    data_loader: dict | None = None  # {type: "huggingface", config: {...}}
    data_parser: dict | str | None = None  # Parser: str or {type: ..., config: {...}}
    
    # Evaluation configuration (shared across all configs)
    evaluation: dict | None = None  # {type: "trace", provider: "groq", config: {...}}
    
    # Data processing pipeline configuration
    data_processing: dict | None = None  # {steps: [{type: "deduplication", config: {...}}]}
    
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
            query_workers=data.get("query_workers", 4),
            max_retry_rounds=data.get("max_retry_rounds", 3),
            retry_delay_seconds=data.get("retry_delay_seconds", 60),
            temp_dir=Path(data.get("temp_dir", "./temp")),
            cache=data.get("cache"),
            data_loader=data.get("data_loader"),
            data_parser=data.get("data_parser"),  # str or dict
            data_processing=data.get("data_processing"),
            evaluation=data.get("evaluation"),
            report_strategy=data.get("report_strategy", "detailed_query"),
        )