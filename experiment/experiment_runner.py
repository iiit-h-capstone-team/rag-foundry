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
from data_sources.processors import DataProcessor
from data_sources.loaders.base import DatasetLoadingConfig
from data_sources.loaders.enums import LoaderType
from parsers import parser_registry, ParserType
from rag.config.enums import Mode
from rag.config.loader import ConfigLoader
from rag.models.pipeline_run_result import PipelineRunResult
from rag.models.query_result import QueryResult
from rag.pipeline.rag_pipeline import RAGPipeline

from reporting import (
    ReportGenerator,
    report_registry,
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
        
        # Create loader via registry
        from data_sources.loaders.registry import loader_registry
        # Trigger registration of HuggingFaceLoader
        from data_sources.loaders.huggingface_loader import HuggingFaceLoader  # noqa: F401
        
        loading_config = DatasetLoadingConfig(
            limit=loader_params.get("limit"),
            use_cache=True,
            cache_dir=str(self.config.cache_dir) if self.config.cache_dir else None
        )
        
        loader = loader_registry.create(
            loader_type,
            dataset_name=loader_params.get("dataset_name"),
            subset=loader_params.get("subset"),
            split=loader_params.get("split", "train"),
            config=loading_config,
            hf_token=loader_params.get("hf_token"),
        )
        
        # Load raw data
        raw_data = loader.load()
        
        # Parse data if parser is specified
        if self.config.data_parser:
            parser_type_str = self.config.data_parser
            try:
                parser = parser_registry.create(parser_type_str)
                processor = DataProcessor(parser_strategy=parser)
                documents = processor.process_dataset(raw_data)
            except (ValueError, KeyError):
                raise ValueError(
                    f"Unknown parser type: {parser_type_str}. "
                    f"Available parsers: {parser_registry.registered_keys()}"
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
        query_workers = self.config.query_workers
        
        # Build ground truth map for all indices
        def _ground_truth(sample):
            return {
                "relevance_score": sample.get("relevance_score", 0.0),
                "utilization_score": sample.get("utilization_score", 0.0),
                "completeness_score": sample.get("completeness_score", 0.0),
                "adherence_score": sample.get("adherence_score", False),
            }
        
        PERMANENT_ERROR = "AllKeysExhaustedException"
        
        def _submit_and_collect(indices):
            """Submit queries for given indices and return (successes, permanent, retryable)."""
            failed_retryable = []
            with ThreadPoolExecutor(max_workers=query_workers) as executor:
                futures = {}
                for i in indices:
                    sample = raw_data[i]
                    future = executor.submit(
                        pipeline.query,
                        sample["question"],
                        i,
                        _ground_truth(sample)
                    )
                    futures[future] = i
                
                for future in as_completed(futures):
                    idx = futures[future]
                    try:
                        result = future.result()
                        jsonl_writer.put(result)
                        # Check if the pipeline returned a failure result
                        if result.metadata.get("status") == "failed":
                            error_type = result.metadata.get("error_type", "")
                            if error_type != PERMANENT_ERROR:
                                failed_retryable.append(idx)
                    except Exception as e:
                        print(f"Error in worker (index {idx}): {e}")
                        failed_retryable.append(idx)
            return failed_retryable
        
        # Initial run
        all_indices = list(range(start_index, end_index))
        # Filter out already-completed indices (resume support)
        pending_indices = [i for i in all_indices if i not in jsonl_writer._completed_indices]
        retryable = _submit_and_collect(pending_indices)
        
        # Retry loop for transient failures
        for retry_round in range(1, self.config.max_retry_rounds + 1):
            if not retryable:
                break
            print(
                f"[{config.name}] Retry round {retry_round}/{self.config.max_retry_rounds}: "
                f"{len(retryable)} retryable failures, waiting {self.config.retry_delay_seconds}s..."
            )
            time.sleep(self.config.retry_delay_seconds)
            
            # Clear retryable indices so the writer will accept new records
            for idx in retryable:
                jsonl_writer.clear_index(idx)
            
            retryable = _submit_and_collect(retryable)
        
        if retryable:
            print(f"[{config.name}] {len(retryable)} queries still failed after all retry rounds")
        
        # Stop progress reporter
        progress_reporter.stop()
        
        # Stop writer thread
        jsonl_writer.stop()
        
        # Deduplicate JSONL (keep last record per index)
        jsonl_writer.deduplicate()
        
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

    def _get_eval_config_and_register(self, rag_config=None):
        """Build EvaluationConfig and register its provider.
        
        Uses experiment-level evaluation config if set, otherwise
        falls back to the per-config evaluation section.
        
        Args:
            rag_config: Optional RAGConfig to fall back to for evaluation
                        config and provider registration.
        
        Returns:
            EvaluationConfig or None
        """
        from evaluation.config import EvaluationConfig
        from providers.provider_manager import ProviderManager
        
        eval_cfg = None
        
        if self.config.evaluation:
            eval_cfg = EvaluationConfig(**self.config.evaluation)
        elif rag_config and rag_config.evaluation:
            eval_cfg = rag_config.evaluation
        
        if eval_cfg is None:
            return None
        
        # Register the provider from any available RAG config
        if eval_cfg.provider:
            # Try to register from the given rag_config's providers
            if rag_config and rag_config.providers:
                provider_config = rag_config.providers.get(eval_cfg.provider)
                if provider_config:
                    ProviderManager.register(
                        provider_name=eval_cfg.provider,
                        provider_type=provider_config.type,
                        config=provider_config,
                    )
        
        return eval_cfg

    def evaluate_runs(self, runs, parallel_runs=False, parallel_config_run=False):
        """Run offline evaluation on JSONL files produced by the pipeline.

        For each run, reads the generation JSONL, evaluates each record
        using the experiment-level evaluation config (or per-config fallback),
        and writes an enriched JSONL with predicted_scores.

        Args:
            runs: List of run dicts from run() or evaluate_config().
            parallel_runs: If True, evaluate multiple configs in parallel.
            parallel_config_run: If True, evaluate records within each
                                 config in parallel.
        """
        if parallel_runs:
            return self._evaluate_runs_parallel(runs, parallel_config_run)
        return self._evaluate_runs_sequential(runs, parallel_config_run)

    def _evaluate_single_run(self, run, parallel_config_run=False):
        """Evaluate a single run dict. Used by both sequential and parallel paths."""
        from evaluation.runner import EvaluationRunner

        config = run["config"]
        jsonl_path = run["jsonl_path"]

        eval_cfg = self._get_eval_config_and_register(rag_config=config)
        if eval_cfg is None:
            print(f"[{config.name}] No evaluation config — skipping evaluation")
            return run

        max_workers = self.config.query_workers if parallel_config_run else 1
        eval_runner = EvaluationRunner(eval_cfg)
        evaluated_path = eval_runner.evaluate_jsonl(
            input_path=jsonl_path,
            output_path=jsonl_path,
            max_workers=max_workers,
        )

        run["jsonl_path"] = evaluated_path
        print(f"[{config.name}] Evaluation complete → {evaluated_path}")
        return run

    def _evaluate_runs_sequential(self, runs, parallel_config_run=False):
        """Evaluate runs one config at a time."""
        return [
            self._evaluate_single_run(run, parallel_config_run)
            for run in runs
        ]

    def _evaluate_runs_parallel(self, runs, parallel_config_run=False):
        """Evaluate runs across configs in parallel."""
        evaluated_runs = []
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(
                    self._evaluate_single_run, run, parallel_config_run
                ): run
                for run in runs
            }
            for future in as_completed(futures):
                try:
                    evaluated_runs.append(future.result())
                except Exception as e:
                    run = futures[future]
                    print(f"[{run['config'].name}] Evaluation failed: {e}")
                    evaluated_runs.append(run)
        return evaluated_runs

    def generate_reports(
        self,
        runs,
    ):
        """Generate reports from JSONL files instead of in-memory results."""
        # Create report strategy using registry
        strategy = report_registry.create(
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

    def evaluate_config(self, config_name: str, parallel: bool = False) -> dict:
        """Evaluate a single config by name.
        
        Finds the JSONL at temp_dir/<config_name>.jsonl, registers the
        evaluation provider, and runs EvaluationRunner.evaluate_jsonl().
        Uses experiment-level evaluation config if set, otherwise falls
        back to per-config. Caching is built-in — already-scored records
        are skipped.
        
        Args:
            config_name: Name of the config to evaluate
            parallel: If True, evaluate records within this config
                      in parallel using query_workers threads.
            
        Returns:
            Run dict with config and jsonl_path
        """
        from evaluation.runner import EvaluationRunner
        
        # Find the config
        configs = self.load_configs()
        config = None
        for cfg in configs:
            if cfg.name == config_name:
                config = cfg
                break
        if config is None:
            raise ValueError(
                f"Config '{config_name}' not found. "
                f"Available: {[c.name for c in configs]}"
            )
        
        jsonl_path = self.config.temp_dir / f"{config_name}.jsonl"
        if not jsonl_path.exists():
            raise FileNotFoundError(
                f"JSONL file not found at {jsonl_path}. Run generation first."
            )
        
        eval_cfg = self._get_eval_config_and_register(rag_config=config)
        if eval_cfg is None:
            print(f"[{config_name}] No evaluation config — skipping")
            return {"config_name": config_name, "config": config, "jsonl_path": jsonl_path}
        
        max_workers = self.config.query_workers if parallel else 1
        eval_runner = EvaluationRunner(eval_cfg)
        evaluated_path = eval_runner.evaluate_jsonl(
            input_path=jsonl_path,
            output_path=jsonl_path,
            max_workers=max_workers,
        )
        
        print(f"[{config_name}] Evaluation complete → {evaluated_path}")
        return {
            "config_name": config_name,
            "config": config,
            "jsonl_path": evaluated_path,
        }

    def compare(self):
        comparison = ComparisonReport.from_directory(
            self.config.report_dir
        )
        comparison.save_csv(
            self.config.report_dir
            / "comparison.csv"
        )
        return comparison