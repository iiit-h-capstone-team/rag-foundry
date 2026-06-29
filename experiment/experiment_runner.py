import json
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from experiment.comparison import ComparisonReport
from experiment.metadata import ExperimentMetadata, ExperimentStatus
from experiment.progress_reporter import ProgressReporter
from rag.persistence.jsonl_writer import JSONLWriter
from ingestion import (
    DataProcessor,
    DatasetLoadingConfig,
    ParserFactory,
    ParserType,
)
from ingestion.loaders.huggingface_loader import HuggingFaceLoader
from rag.config.enums import Mode
from rag.config.loader import ConfigLoader
from rag.models.pipeline_run_result import PipelineRunResult
from rag.models.query_result import QueryResult
from rag.pipeline.rag_pipeline import RAGPipeline

from reporting import (
    ReportGenerator,
    ReportStrategyFactory,
)


class ExperimentRunner:
    def __init__(self, experiment_config):
        self.config = experiment_config

        self.config.report_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        self.config.temp_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def load_configs(self):
        configs = []
        for path in sorted(
            self.config.config_dir.glob("*.yaml")
        ):
            cfg = ConfigLoader.load(path)
            cfg.mode = Mode.TEST
            cfg.cache.cache_dir = str(
                self.config.cache_dir
            )
            configs.append(cfg)
        return configs

    def load_data(self):
        """
        Generic data loading method based on YAML configuration.
        
        Reads data_loader and data_parser from experiment config and:
        1. Instantiates the appropriate loader based on type
        2. Loads raw data using the loader
        3. Parses the data using the specified parser
        4. Returns both documents and raw_data
        
        Returns:
            tuple: (documents, raw_data)
                - documents: List of parsed Document objects
                - raw_data: List of raw dataset samples
        
        Raises:
            ValueError: If data_loader config is missing or invalid
        """
        if not self.config.data_loader:
            raise ValueError(
                "data_loader configuration is missing. "
                "Please add data_loader section to experiment config."
            )
        
        loader_config = self.config.data_loader
        loader_type = loader_config.get("type")
        loader_params = loader_config.get("config", {})
        
        # Create loader based on type
        if loader_type == "huggingface":
            dataset_name = loader_params.get("dataset_name")
            subset = loader_params.get("subset")
            split = loader_params.get("split", "train")
            limit = loader_params.get("limit")
            hf_token = loader_params.get("hf_token")
            
            loading_config = DatasetLoadingConfig(
                limit=limit,
                use_cache=True,
                cache_dir=str(self.config.cache_dir) if self.config.cache_dir else None
            )
            
            loader = HuggingFaceLoader(
                dataset_name=dataset_name,
                subset=subset,
                split=split,
                config=loading_config,
                hf_token=hf_token
            )
        else:
            raise ValueError(
                f"Unknown loader type: {loader_type}. "
                f"Supported types: huggingface"
            )
        
        # Load raw data
        raw_data = loader.load()
        
        # Parse data if parser is specified
        if self.config.data_parser:
            parser_type_str = self.config.data_parser
            try:
                parser_type = ParserType(parser_type_str)
                parser = ParserFactory.create_parser(parser_type)
                processor = DataProcessor(parser_strategy=parser)
                documents = processor.process_dataset(raw_data)
            except ValueError:
                raise ValueError(
                    f"Unknown parser type: {parser_type_str}. "
                    f"Available parsers: {ParserFactory.available_parsers()}"
                )
        else:
            # If no parser specified, return empty documents list
            documents = []
        
        return documents, raw_data

    def _run_config(
        self,
        config,
        documents,
        raw_data,
    ):
        """Run a single config with parallel query execution."""
        # Resolve query range
        start_index = (
            config.start_index
            if config.start_index is not None
            else self.config.start_index
        )
        end_index = (
            config.end_index
            if config.end_index is not None
            else self.config.end_index
        )
        if end_index is None:
            end_index = len(raw_data)
        
        # Create JSONL writer
        jsonl_path = self.config.temp_dir / f"{config.name}.jsonl"
        jsonl_writer = JSONLWriter(jsonl_path)
        jsonl_writer.start()
        
        # Create pipeline and build index once
        pipeline = RAGPipeline(config, jsonl_path=jsonl_path)
        pipeline.build_index(documents)
        
        # Create metadata
        dataset_name = self.config.data_loader.get("config", {}).get("dataset_name", "unknown") if self.config.data_loader else "unknown"
        metadata = ExperimentMetadata(
            dataset=dataset_name,
            config_name=config.name,
            start_index=start_index,
            end_index=end_index,
            total_queries=end_index - start_index,
            created_at=datetime.utcnow().isoformat(),
            status=ExperimentStatus.RUNNING,
        )
        metadata_path = self.config.temp_dir / f"{config.name}_metadata.json"
        metadata.save(metadata_path)
        
        # Start progress reporter
        show_progress = config.logging_config.show_progress if hasattr(config.logging_config, 'show_progress') else True
        total_queries = end_index - start_index
        progress_reporter = ProgressReporter(
            total_queries=total_queries,
            jsonl_writer=jsonl_writer,
            show_progress=show_progress
        )
        progress_reporter.start()
        
        # Submit query tasks to ThreadPoolExecutor
        max_workers = self.config.max_workers
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i in range(start_index, end_index):
                sample = raw_data[i]
                # Extract ground truth scores
                ground_truth = {
                    "relevance_score": sample.get("relevance_score", 0.0),
                    "utilization_score": sample.get("utilization_score", 0.0),
                    "completeness_score": sample.get("completeness_score", 0.0),
                    "adherence_score": sample.get("adherence_score", False),
                }
                future = executor.submit(
                    pipeline.query,
                    sample["question"],
                    i,
                    ground_truth
                )
                futures.append(future)
            
            # Wait for all futures to complete and write results
            for future in as_completed(futures):
                try:
                    result = future.result()
                    jsonl_writer.put(result)
                except Exception as e:
                    print(f"Error in worker: {e}")
        
        # Stop progress reporter
        progress_reporter.stop()
        
        # Stop writer thread
        jsonl_writer.stop()
        
        # Update metadata
        metadata.update_status(ExperimentStatus.COMPLETED)
        metadata.save(metadata_path)
        
        # Return summary statistics instead of full results
        stats = jsonl_writer.get_stats()
        return {
            "config_name": config.name,
            "config": config,
            "total_written": stats["total_written"],
            "highest_continuous_index": stats["highest_continuous_index"],
            "jsonl_path": jsonl_path,
        }

    def run(
        self,
        documents,
        raw_data,
    ):
        configs = self.load_configs()
        if not self.config.parallel:
            return [
                self._run_config(
                    cfg,
                    documents,
                    raw_data,
                )
                for cfg in configs
            ]
        runs = []

        with ThreadPoolExecutor(
            max_workers=self.config.max_workers
        ) as executor:
            futures = {
                executor.submit(
                    self._run_config,
                    cfg,
                    documents,
                    raw_data,
                ): cfg.name
                for cfg in configs
            }
            for future in as_completed(futures):
                run = future.result()
                print(
                    f"Finished {run.config.name}"
                )
                runs.append(run)
        return runs

    def generate_reports(
        self,
        runs,
    ):
        """Generate reports from JSONL files instead of in-memory results."""
        # Create report strategy using factory pattern
        strategy = ReportStrategyFactory.create_strategy(
            self.config.report_strategy
        )
        
        generator = ReportGenerator(strategy)
        reports = []
        for run in runs:
            # Generate report from JSONL file
            jsonl_path = run["jsonl_path"]
            config = run["config"]
            
            # Load records from JSONL and create PipelineRunResult-like structure
            records = self._load_records_from_jsonl(jsonl_path)
            
            # Create a PipelineRunResult for compatibility
            pipeline_run_result = PipelineRunResult(
                records=records,
                config=config,
            )
            
            report = generator.generate(pipeline_run_result)
            report.save_json(
                self.config.report_dir
                / f"{config.name}.json"
            )
            reports.append(report)
        return reports
    
    def _load_records_from_jsonl(self, jsonl_path: Path):
        """Stream query records from JSONL file one at a time."""
        from rag.models.query_result import QueryResult
        
        records = []
        with open(jsonl_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    # Skip failed records
                    if record.get("metadata", {}).get("status") == "failed":
                        continue
                    
                    # Convert to QueryResult using from_dict
                    query_result = QueryResult.from_dict(record)
                    records.append(query_result)
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error loading record from JSONL: {e}")
                    continue
        
        return records

    def compare(self):
        comparison = ComparisonReport.from_directory(
            self.config.report_dir
        )
        comparison.save_csv(
            self.config.report_dir
            / "comparison.csv"
        )
        return comparison