"""
Examples of using the data loader system.

Note: Data loader handles loading and parsing.
Chunking is handled by rag.chunking strategies via StrategyFactory.
"""

from data_loader import (
    DataLoaderFactory,
    DataProcessor,
    DataLoadingConfig
)


def example_load_covidqa():
    """Example: Load CovidQA dataset."""
    print("=" * 60)
    print("Example 1: Loading CovidQA Dataset")
    print("=" * 60)

    loader = DataLoaderFactory.create_covidqa_loader(
        split="test",
        limit=5  # Load first 5 samples
    )

    data = loader.load()
    print(f"✅ Loaded {len(data)} samples\n")

    # Print dataset info
    info = loader.info()
    print(f"Dataset Info:")
    print(f"  Source: {info['source']}")
    print(f"  Dataset: {info['dataset_name']}")
    print(f"  Split: {info['split']}")
    print(f"  Samples: {info['num_samples']}")
    print(f"  Keys: {info['keys'][:5]}...\n")  # Show first 5 keys

    # Print first sample
    sample = loader.load_sample(0)
    print(f"First Sample:")
    print(f"  Question: {sample.get('question', 'N/A')[:100]}...")
    print(f"  Documents: {len(sample.get('documents', []))} documents")
    print()


def example_parse_documents():
    """Example: Parse documents from dataset."""
    print("=" * 60)
    print("Example 2: Parse Documents")
    print("=" * 60)

    # Load data
    loader = DataLoaderFactory.create_covidqa_loader(split="test", limit=2)
    data = loader.load()

    # Parse documents
    print("\n📄 Parsing documents:")
    parsed_docs = DataProcessor.process_dataset(data)

    print(f"✅ Parsed {len(parsed_docs)} documents\n")

    # Print first few parsed documents
    for i, doc in enumerate(parsed_docs[:3]):
        print(f"Document {i+1}:")
        print(f"  Title: {doc.title[:50]}...")
        print(f"  Content: {doc.content[:100]}...")
        print(f"  Metadata: {doc.metadata}\n")


def example_convert_to_rag_documents():
    """Example: Convert to RAG Document format."""
    print("=" * 60)
    print("Example 3: Convert to RAG Document Format")
    print("=" * 60)

    # Load and parse
    loader = DataLoaderFactory.create_covidqa_loader(split="test", limit=1)
    data = loader.load()
    parsed_docs = DataProcessor.process_dataset(data)

    # Convert to rag.models.Document
    print("\n📄 Converting to RAG Document format:")
    try:
        documents = DataProcessor.convert_to_rag_documents(parsed_docs)
        print(f"✅ Converted {len(documents)} documents\n")

        for i, doc in enumerate(documents[:2]):
            print(f"RAG Document {i+1}:")
            print(f"  Title: {doc.title[:50]}...")
            print(f"  Content: {doc.content[:100]}...")
            print(f"  Metadata: {doc.metadata}\n")
    except ImportError:
        print("⚠️  rag.models.Document not available in this context\n")


def example_batch_loading():
    """Example: Load data in batches."""
    print("=" * 60)
    print("Example 4: Batch Loading")
    print("=" * 60)

    loader = DataLoaderFactory.create_covidqa_loader(
        split="test",
        limit=10
    )

    # Load batch
    batch = loader.load_batch(start=0, end=5)
    print(f"✅ Loaded batch of {len(batch)} samples")

    # Load next batch
    batch_2 = loader.load_batch(start=5, end=10)
    print(f"✅ Loaded next batch of {len(batch_2)} samples\n")


def example_available_datasets():
    """Example: Check available datasets."""
    print("=" * 60)
    print("Example 5: Available Datasets")
    print("=" * 60)

    datasets = DataLoaderFactory.available_datasets()
    print(f"Available specific loaders: {datasets}\n")

    # Can also load other datasets generically
    print("Note: You can also load other RAGBench datasets generically:")
    print("  loader = DataLoaderFactory.create_ragbench_loader('any_dataset_name')\n")


def example_integration_with_rag_pipeline():
    """Example: Integration with RAG pipeline (conceptual)."""
    print("=" * 60)
    print("Example 6: Integration with RAG Pipeline")
    print("=" * 60)

    print("""
Integration Pattern:
────────────────────

1. Load data with DataLoader
   loader = DataLoaderFactory.create_covidqa_loader()
   data = loader.load()

2. Parse documents
   parsed_docs = DataProcessor.process_dataset(data)

3. Convert to RAG Documents
   documents = DataProcessor.convert_to_rag_documents(parsed_docs)

4. Create RAG Document objects with the full content
   from rag.models.document import Document
   rag_docs = [
       Document(
           title=doc.title,
           content=doc.content,
           metadata=doc.metadata
       )
       for doc in parsed_docs
   ]

5. Use StrategyFactory to apply chunking
   from rag.factory.strategy_factory import StrategyFactory
   from rag.config.config import ChunkingConfig, SentenceChunkingConfig
   from rag.config.enums import ChunkingType

   chunker = StrategyFactory.create_chunker(
       ChunkingConfig(
           type=ChunkingType.SENTENCE,
           config=SentenceChunkingConfig(max_words=100)
       )
   )

   chunks = []
   for rag_doc in rag_docs:
       doc_chunks = chunker.chunk(rag_doc)
       chunks.extend(doc_chunks)

6. Build embeddings and index
   embedder = StrategyFactory.create_embedder(...)
   embeddings = embedder.embed([c.text for c in chunks])
   vector_store.add(embeddings, chunks)

7. Use complete RAG pipeline with config
   from examples.complete_pipeline_example import RAGPipeline
   from rag.config.loader import ConfigLoader

   config = ConfigLoader.load('config/rag_config_high_quality.yaml')
   pipeline = RAGPipeline(config, clients)
   pipeline.build_index(rag_docs)
   result = pipeline.query("Your question?")
    """)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DATA LOADER EXAMPLES")
    print("=" * 60 + "\n")

    try:
        example_load_covidqa()
    except Exception as e:
        print(f"⚠️  Example 1 failed: {e}\n")

    try:
        example_parse_documents()
    except Exception as e:
        print(f"⚠️  Example 2 failed: {e}\n")

    try:
        example_convert_to_rag_documents()
    except Exception as e:
        print(f"⚠️  Example 3 failed: {e}\n")

    try:
        example_batch_loading()
    except Exception as e:
        print(f"⚠️  Example 4 failed: {e}\n")

    try:
        example_available_datasets()
    except Exception as e:
        print(f"⚠️  Example 5 failed: {e}\n")

    try:
        example_integration_with_rag_pipeline()
    except Exception as e:
        print(f"⚠️  Example 6 failed: {e}\n")

    print("=" * 60)
    print("EXAMPLES COMPLETE")
    print("=" * 60)

