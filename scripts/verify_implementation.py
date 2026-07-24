"""Verify BM25 + Processing Pipeline implementation."""

import logging
logging.basicConfig(level=logging.INFO)

print("=" * 60)
print("VERIFICATION: BM25 + Processing Pipeline")
print("=" * 60)

# 1. Verify imports
print("\n--- 1. Imports ---")
from data_sources.processors import (
    DataProcessor, ProcessingStep, ProcessingStepType,
    processing_step_registry, ProcessingPipeline
)
print("All imports OK")

# 2. Verify registry
print("\n--- 2. Registry ---")
import data_sources.processors.strategies.deduplication  # noqa
print("Registry keys:", processing_step_registry.registered_keys())

# 3. Test deduplication step (content_hash)
print("\n--- 3. Deduplication (content_hash) ---")
from rag.models.document import Document
docs = [
    Document(title="T1", content="Hello world", metadata={"id": 1}),
    Document(title="T2", content="Hello world", metadata={"id": 2}),  # dup content
    Document(title="T3", content="Unique doc", metadata={"id": 3}),
    Document(title="T1", content="Hello world", metadata={"id": 4}),  # dup content
]
step = processing_step_registry.create("deduplication", config={"strategy": "content_hash"})
result = step.process(docs)
print(f"Dedup: {len(docs)} -> {len(result)} documents")
assert len(result) == 2, f"Expected 2, got {len(result)}"
print("PASS")

# 4. Test deduplication step (title_content_hash)
print("\n--- 4. Deduplication (title_content_hash) ---")
step2 = processing_step_registry.create("deduplication", config={"strategy": "title_content_hash"})
result2 = step2.process(docs)
print(f"Dedup (title+content): {len(docs)} -> {len(result2)} documents")
assert len(result2) == 3, f"Expected 3, got {len(result2)}"
print("PASS")

# 5. Test pipeline from_config
print("\n--- 5. ProcessingPipeline.from_config ---")
pipeline = ProcessingPipeline.from_config({
    "steps": [
        {"type": "deduplication", "config": {"strategy": "content_hash"}}
    ]
})
result3 = pipeline.run(docs)
print(f"Pipeline: {len(docs)} -> {len(result3)} documents")
assert len(result3) == 2
print("PASS")

# 6. Test BM25Store
print("\n--- 6. BM25Store ---")
from rag.modules.search.bm25_store import BM25Store
from rag.models.chunk import Chunk
chunks = [
    Chunk(text="COVID-19 is a respiratory disease caused by SARS-CoV-2", metadata={}),
    Chunk(text="Influenza vaccines are administered annually", metadata={}),
    Chunk(text="The coronavirus pandemic started in Wuhan China", metadata={}),
    Chunk(text="Handwashing prevents the spread of infections", metadata={}),
]
store = BM25Store(chunks)
results = store.search("coronavirus pandemic", top_k=3)
print(f"BM25 search returned {len(results)} results:")
for idx, score in results:
    print(f"  idx={idx}, score={score:.4f}: {chunks[idx].text[:60]}...")
assert len(results) > 0, "BM25 should return results"
assert results[0][0] == 2, f"Top result should be idx=2, got {results[0][0]}"
print("PASS")

# 7. Test ExperimentConfig loads data_processing
print("\n--- 7. ExperimentConfig ---")
from experiment.experiment_config import ExperimentConfig
cfg = ExperimentConfig.load("experiment_configs/covidqa_experiment.yaml")
assert cfg.data_processing is not None, "data_processing should be set"
assert cfg.data_processing["steps"][0]["type"] == "deduplication"
print(f"data_processing: {cfg.data_processing}")
print("PASS")

# 8. Test SparseSearchStrategy accepts callable bm25_store
print("\n--- 8. SparseSearchStrategy lazy ref ---")
from rag.modules.search.strategies.sparse.strategy import SparseSearchStrategy
from rag.modules.search.strategies.sparse.config import SparseSearchConfig

class FakePipeline:
    bm25_store = None

fake = FakePipeline()
sparse = SparseSearchStrategy(
    config=SparseSearchConfig(top_k=5),
    vector_store=None,
    bm25_store=lambda: fake.bm25_store,
)
# Before setting store, should return empty
assert sparse.search(["test"]) == [], "Should return [] when store is None"
print("Lazy ref returns [] when store is None: PASS")

print("\n" + "=" * 60)
print("ALL TESTS PASSED")
print("=" * 60)
