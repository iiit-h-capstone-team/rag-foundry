"""Standalone evaluation runner.

Reads JSONL files produced by the RAG pipeline (retrieval + generation),
runs evaluation strategies offline, and writes enriched JSONL with scores.

This decouples evaluation from the pipeline so it can:
- Use its own API key pool / rate-limit budget
- Run sequentially to avoid rate limiting with heavier models
- Be retried independently without re-running generation
"""

import json
import logging
import time
from pathlib import Path
from typing import Optional

from evaluation.registry import evaluation_registry
from evaluation.config import EvaluationConfig
from providers.provider_manager import ProviderManager

logger = logging.getLogger(__name__)


class EvaluationRunner:
    """Run evaluation offline on JSONL files.

    Reads each record from a JSONL file, runs the configured evaluation
    strategy, appends predicted_scores to metadata, and writes an
    enriched JSONL file.
    """

    def __init__(
        self,
        evaluation_config: EvaluationConfig,
        provider_name: str = None,
    ):
        """Initialize the evaluation runner.

        Args:
            evaluation_config: Evaluation configuration with type, provider, and strategy config.
            provider_name: Name of the provider to use. Defaults to evaluation_config.provider.
        """
        self.eval_config = evaluation_config
        self.provider_name = provider_name or evaluation_config.provider

        # Create evaluator via registry
        provider = ProviderManager.get_provider(self.provider_name)
        self.evaluator = evaluation_registry.create(
            self.eval_config.type,
            config=self.eval_config.config,
            provider=provider,
        )

    def evaluate_jsonl(
        self,
        input_path: str | Path,
        output_path: Optional[str | Path] = None,
        max_workers: int = 1,
    ) -> Path:
        """Evaluate all records in a JSONL file.

        Args:
            input_path: Path to JSONL file with generation results.
            output_path: Path for enriched output. Defaults to <input>_evaluated.jsonl.
            max_workers: Number of parallel workers for evaluation.
                         1 = sequential (default), >1 = parallel.

        Returns:
            Path to the enriched JSONL file.
        """
        import tempfile
        from concurrent.futures import ThreadPoolExecutor, as_completed

        input_path = Path(input_path)
        if output_path is None:
            output_path = input_path.with_name(
                input_path.stem + "_evaluated" + input_path.suffix
            )
        output_path = Path(output_path)

        records = []
        with open(input_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))

        logger.info("Evaluating %d records from %s (workers=%d)", len(records), input_path, max_workers)
        evaluated = 0
        skipped = 0

        def _should_skip(record):
            """Return True if this record should be skipped."""
            metadata = record.get("metadata", {})
            # Skip only if generation was successful AND evaluation succeeded
            if metadata.get("status") != "success":
                return True
            # Skip only if already has predicted_scores (successful evaluation)
            if "predicted_scores" in metadata:
                return True
            # Retry records with evaluation errors (don't skip them)
            return False

        def _evaluate_record(idx, record):
            """Evaluate a single record. Returns (idx, record)."""
            metadata = record.get("metadata", {})
            retrieved_docs = []
            for doc in record.get("retrieved_docs", []):
                retrieved_docs.append({
                    "text": doc.get("content", doc.get("text", "")),
                    **{k: v for k, v in doc.items() if k not in ("content", "text")},
                })

            try:
                eval_start = time.time()
                scores = self.evaluator.evaluate(
                    query=record["query"],
                    retrieved_docs=retrieved_docs,
                    response=record["answer"],
                )
                eval_ms = (time.time() - eval_start) * 1000

                metadata["predicted_scores"] = scores
                metadata.setdefault("latencies", {})["evaluation_ms"] = eval_ms
                record["metadata"] = metadata

                logger.debug(
                    "Record %d/%d evaluated (%.0fms)",
                    idx + 1, len(records), eval_ms,
                )

            except Exception as e:
                logger.warning("Record %d evaluation failed: %s", idx + 1, e)
                metadata["evaluation_error"] = str(e)
                metadata["evaluation_error_type"] = type(e).__name__
                record["metadata"] = metadata

            return idx, record

        # Identify which records need evaluation
        pending = []
        for i, record in enumerate(records):
            if _should_skip(record):
                skipped += 1
            else:
                pending.append(i)

        # Evaluate pending records (parallel or sequential)
        if max_workers > 1 and pending:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(_evaluate_record, i, records[i]): i
                    for i in pending
                }
                for future in as_completed(futures):
                    idx, record = future.result()
                    records[idx] = record
                    if "predicted_scores" in record.get("metadata", {}):
                        evaluated += 1
        else:
            for i in pending:
                _, record = _evaluate_record(i, records[i])
                records[i] = record
                if "predicted_scores" in record.get("metadata", {}):
                    evaluated += 1

        # Write to a temp file first, then atomically rename to output_path.
        # This prevents data loss if evaluation crashes mid-write.
        tmp_fd, tmp_path = tempfile.mkstemp(
            suffix=".jsonl", dir=output_path.parent
        )
        try:
            with open(tmp_fd, "w", encoding="utf-8") as out:
                for record in records:
                    out.write(json.dumps(record, ensure_ascii=False) + "\n")

            # Atomic rename — only replaces the original after full success
            Path(tmp_path).replace(output_path)

        except BaseException:
            # Clean up temp file on any failure
            Path(tmp_path).unlink(missing_ok=True)
            raise

        logger.info(
            "Evaluation complete: %d evaluated, %d skipped → %s",
            evaluated, skipped, output_path,
        )
        return output_path
