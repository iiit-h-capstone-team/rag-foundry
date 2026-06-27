from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from experiment.comparison import ComparisonReport
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
        pipeline = RAGPipeline(config)
        pipeline.build_index(documents)
        records = []
        for sample in raw_data[: self.config.num_queries]:
            result = pipeline.query(
                sample["question"]
            )
            records.append(
                QueryResult(
                    query=sample["question"],
                    retrieved_docs=result["retrieved_docs"],
                    answer=result["response"],
                    metadata={
                        "predicted_scores": result["scores"],
                        "ground_truth_scores": {
                            "relevance_score": sample.get("relevance_score", 0.0),
                            "utilization_score": sample.get("utilization_score", 0.0),
                            "completeness_score": sample.get("completeness_score", 0.0),
                            "adherence_score": sample.get("adherence_score", False),
                        },
                    },
                )
            )
        return PipelineRunResult(
            records=records,
            config=config,
        )

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
        # Create report strategy using factory pattern
        strategy = ReportStrategyFactory.create_strategy(
            self.config.report_strategy
        )
        
        generator = ReportGenerator(strategy)
        reports = []
        for run in runs:
            report = generator.generate(run)
            report.save_json(
                self.config.report_dir
                / f"{run.config.name}.json"
            )
            reports.append(report)
        return reports

    def compare(self):
        comparison = ComparisonReport.from_directory(
            self.config.report_dir
        )
        comparison.save_csv(
            self.config.report_dir
            / "comparison.csv"
        )
        return comparison