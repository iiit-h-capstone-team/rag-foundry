# Complete Guide: Ingestion Layer and RAG Pipeline

This guide provides comprehensive documentation for using the ingestion layer and RAG pipeline in a unified, easy-to-follow format.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Ingestion Layer](#ingestion-layer)
3. [RAG Pipeline](#rag-pipeline)
4. [Complete Workflow Example](#complete-workflow-example)
5. [Configuration](#configuration)
6. [Migration Guide](#migration-guide)
7. [Best Practices](#best-practices)

---

## Architecture Overview

The system is divided into two distinct layers with clear separation of concerns:

### Ingestion Layer (`ingestion/`)
Handles data loading, parsing, and preprocessing. Responsible for:
- Loading datasets from various sources (RAGBench, local files, APIs)
- Parsing documents from different formats (title/passage, markdown, JSON, PDF)
- Transforming raw data into canonical `Document` objects

### RAG Layer (`rag/`)
Handles retrieval-augmented generation. Responsible for:
- Document chunking strategies
- Text embedding
- Vector storage
- Retrieval and reranking
- Response generation
- Evaluation

### Why This Separation?

**Single Responsibility Principle:**
- Ingestion handles data sources and formats
- RAG handles retrieval and generation logic

**Open/Closed Principle:**
- Easy to add new data sources without modifying RAG code
- Easy to add new RAG strategies without modifying ingestion code

**Dependency Inversion:**
- RAG depends on canonical `Document` objects, not data formats
- Ingestion produces canonical objects that RAG can consume

**Extensibility:**
- Support for future ingestion sources: PDFs, Confluence, Slack, JSON, Markdown
- Support for future RAG strategies: new chunking, embedding, retrieval methods

### Data Flow

```
Dataset Source (RAGBench, Local Files, APIs)
    ↓
Ingestion Layer
    ├── DatasetLoader (loaders/)
    │   └── RAGBenchLoader, LocalFileLoader, etc.
    ├── DataProcessor (processors/)
    │   └── Orchestrates parsing workflow
    └── ParsingStrategy (parsers/)
        ├── TitlePassageParser
        ├── MarkdownParser (future)
        └── JsonParser (future)
    ↓
Canonical Document (rag.models.Document)
    ├── title: str
    ├── content: str
    └── metadata: dict
    ↓
RAG Pipeline
    ├── ChunkingStrategy (chunking/)
    ├── EmbeddingStrategy (embedding/)
    ├── VectorStore (vectorstores/)
    ├── RetrievalStrategy (retrieval/)
    ├── GenerationStrategy (generation/)
    └── EvaluationStrategy (evaluation/)
    ↓
Query Results and Responses
```

---

## Ingestion Layer

### Directory Structure

```
ingestion/
├── loaders/
│   ├── base.py              # DatasetLoader ABC, DatasetLoadingConfig
│   └── ragbench_loader.py   # RAGBench-specific loaders
├── parsers/
│   ├── base.py              # ParsingStrategy ABC
│   ├── title_passage_parser.py  # Title/Passage format parser
│   └── strategy_factory.py  # ParserFactory, ParserType enum
├── processors/
│   └── data_processor.py    # DataProcessor orchestration
└── __init__.py
```

### Loaders

#### Base Classes

**DatasetLoadingConfig**
```python
from ingestion import DatasetLoadingConfig

config = DatasetLoadingConfig(
    cache_dir=None,      # Optional cache directory
    use_cache=True,      # Enable in-memory caching
    limit=100            # Limit number of samples
)
```

**DatasetLoader (Abstract)**
```python
from ingestion import DatasetLoader

class DatasetLoader(ABC):
    def load() -> List[Dict[str, Any]]      # Load all data
    def load_sample(index) -> Dict          # Load single sample
    def load_batch(start, end) -> List      # Load batch
    def info() -> Dict                      # Dataset metadata
```

#### RAGBench Loaders

**RAGBenchLoader** (Generic)
```python
from ingestion import RAGBenchLoader, DatasetLoadingConfig

loader = RAGBenchLoader(
    dataset_name="covidqa",
    split="test",
    config=DatasetLoadingConfig(limit=100),
    hf_token="your_hf_token"  # Optional
)

raw_data = loader.load()
```

**Specific Loaders** (Pre-configured)
```python
from ingestion import (
    RAGBenchCovidQALoader,
    RAGBenchFeverousLoader,
    RAGBenchHotpotQALoader
)

# CovidQA
loader = RAGBenchCovidQALoader(split="test", limit=100)

# FEVEROUS
loader = RAGBenchFeverousLoader(split="test", limit=100)

# HotpotQA
loader = RAGBenchHotpotQALoader(split="test", limit=100)

# Load data
raw_data = loader.load()

# Get dataset info
info = loader.info()
print(f"Source: {info['source']}")
print(f"Dataset: {info['dataset_name']}")
print(f"Samples: {info['num_samples']}")

# Load single sample
sample = loader.load_sample(0)
print(f"Question: {sample['question']}")

# Load batch
batch = loader.load_batch(start=0, end=10)
```

### Parsers

#### Parser Strategy Pattern

The ingestion layer uses the Strategy Pattern for document parsing. This allows for easy extension with new parsers without modifying the processor logic.

**ParserType Enum**
```python
from ingestion import ParserType

# Available parsers
ParserType.TITLE_PASSAGE  # Parses "Title: ... Passage: ..." format
# Future parsers:
# ParserType.MARKDOWN
# ParserType.JSON
# ParserType.PDF
```

**ParserFactory**
```python
from ingestion import ParserFactory, ParserType

# Create parser
parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)

# Check available parsers
available = ParserFactory.available_parsers()
# ['title_passage']

# Register custom parser (for extension)
class CustomParser(ParsingStrategy):
    def parse(self, raw_document, metadata=None):
        # Custom parsing logic
        pass

ParserFactory.register_parser(ParserType.CUSTOM, CustomParser)
```

#### TitlePassageParser

Parses documents in the standard RAGBench format:
```
Title: <title text>
Passage: <passage text>
```

```python
from ingestion import ParserFactory, ParserType

parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)

# Parse a document
raw_doc = """Title: COVID-19 Overview
Passage: COVID-19 is a disease caused by the SARS-CoV-2 virus."""

document = parser.parse(raw_doc, metadata={'source': 'ragbench'})

# Result is a canonical rag.models.Document
print(document.title)    # "COVID-19 Overview"
print(document.content)  # "COVID-19 is a disease caused by..."
print(document.metadata) # {'source': 'ragbench', 'parser_type': 'title_passage'}
```

### Processors

#### DataProcessor

Orchestrates the transformation from raw dataset samples to canonical Document objects.

```python
from ingestion import DataProcessor, ParserFactory, ParserType

# Create parser strategy
parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)

# Create processor with parser
processor = DataProcessor(parser_strategy=parser)

# Process dataset
raw_data = loader.load()  # From DatasetLoader
documents = processor.process_dataset(raw_data)

# Process single sample
sample = loader.load_sample(0)
documents = processor.process_sample(sample)
```

**DataProcessor Responsibilities:**
- Iterates over dataset samples
- Extracts raw documents from samples
- Creates metadata (doc_id, sample_index, source)
- Delegates parsing to the parser strategy
- Returns List[Document] (canonical objects)

**DataProcessor Does NOT:**
- Contain parsing logic (delegated to parser strategy)
- Perform chunking (handled by RAG layer)
- Perform embedding (handled by RAG layer)

---

## RAG Pipeline

### Directory Structure

```
rag/
├── models/
│   ├── document.py          # Document dataclass
│   ├── chunk.py             # Chunk dataclass
│   └── retrieval_result.py  # RetrievalResult dataclass
├── chunking/
│   ├── base.py              # ChunkingStrategy ABC
│   ├── sentence_chunking.py
│   ├── fixed_window_chunking.py
│   └── token_chunking.py
├── embedding/
│   ├── base.py              # EmbeddingStrategy ABC
│   ├── bge_embedding.py
│   ├── openai_embedding.py
│   └── local_embedding.py
├── vectorstores/
│   ├── base.py              # VectorStore ABC
│   └── faiss_store.py       # FAISS implementation
├── retrieval/
│   ├── base.py              # RetrievalStrategy ABC
│   ├── dense_retrieval.py
│   ├── dense_rerank.py
│   └── hybrid_retrieval.py
├── generation/
│   ├── base.py              # GenerationStrategy ABC
│   ├── groq_generation.py
│   └── openai_generation.py
├── evaluation/
│   ├── base.py              # EvaluationStrategy ABC
│   └── trace_evaluation.py
├── pipeline/
│   └── complete_pipeline.py  # RAGPipeline orchestration
├── config/
│   ├── config.py            # RAGConfig dataclass
│   ├── enums.py             # Type enums
│   └── loader.py            # ConfigLoader
└── factory/
    └── strategy_factory.py  # StrategyFactory
```

### Models

#### Document (Canonical Object)

```python
from rag.models.document import Document

document = Document(
    title="Document Title",
    content="Document content...",
    metadata={
        'doc_id': 'sample_0_doc_0',
        'sample_index': 0,
        'source': 'ragbench'
    }
)
```

#### Chunk

```python
from rag.models.chunk import Chunk

chunk = Chunk(
    text="Chunk text...",
    metadata={
        'title': 'Document Title',
        'doc_id': 'sample_0_doc_0',
        'chunk_id': 'sample_0_doc_0_chunk_0'
    }
)
```

### Chunking Strategies

#### Available Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Sentence | Splits by sentence boundaries | Natural text with clear structure |
| Fixed Window | Fixed character windows | Uniform processing requirements |
| Token | Word-based token counting | API-constrained scenarios |

#### Usage

```python
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import ChunkingType

# Sentence-based chunking
chunker = StrategyFactory.create_chunker(
    ChunkingType.SENTENCE,
    max_words=100,
    overlap_sentences=1
)

# Fixed window chunking
chunker = StrategyFactory.create_chunker(
    ChunkingType.FIXED_WINDOW,
    window_size=256,
    overlap=50
)

# Token-based chunking
chunker = StrategyFactory.create_chunker(
    ChunkingType.TOKEN,
    max_tokens=200,
    overlap_tokens=20
)

# Chunk documents
chunks = chunker.chunk(document)
```

### Embedding Strategies

#### Available Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| BGE | BAAI/BGE models | Production RAG systems |
| OpenAI | OpenAI API embeddings | State-of-the-art performance |
| Local | Local models (MiniLM) | Local deployment, cost savings |

#### Usage

```python
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import EmbeddingType
from sentence_transformers import SentenceTransformer

# BGE embedding
embedder = StrategyFactory.create_embedder(
    EmbeddingType.BGE,
    model='BAAI/bge-large-en-v1.5'
)

# OpenAI embedding
import openai
client = openai.OpenAI(api_key="your_key")
embedder = StrategyFactory.create_embedder(
    EmbeddingType.OPENAI,
    client=client,
    model='text-embedding-3-small'
)

# Local embedding
embedder = StrategyFactory.create_embedder(
    EmbeddingType.LOCAL,
    model_name='all-MiniLM-L6-v2'
)

# Generate embeddings
texts = ["text 1", "text 2", "text 3"]
embeddings = embedder.embed(texts)
```

### Vector Stores

#### FAISS Vector Store

```python
from rag.vectorstores.faiss_store import FaissVectorStore

# Create vector store
vector_store = FaissVectorStore(dimension=768)

# Add embeddings
vector_store.add(embeddings, documents)

# Search
results = vector_store.search(query_embedding, top_k=5)
```

### Retrieval Strategies

#### Available Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Dense | Simple dense similarity | Fast retrieval with good recall |
| Dense + Rerank | Dense + cross-encoder reranking | High precision results |
| Hybrid | Combines dense and sparse (BM25) | Balanced precision/recall |

#### Usage

```python
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import RetrievalType

# Dense retrieval
retriever = StrategyFactory.create_retriever(
    RetrievalType.DENSE,
    embedder=embedder,
    vector_store=vector_store
)

# Dense + Rerank retrieval
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

retriever = StrategyFactory.create_retriever(
    RetrievalType.DENSE_RERANK,
    embedder=embedder,
    vector_store=vector_store,
    reranker=reranker,
    initial_k=20
)

# Hybrid retrieval
from rank_bm25 import BM25Okapi
bm25_store = BM25Okapi(corpus)

retriever = StrategyFactory.create_retriever(
    RetrievalType.HYBRID,
    embedder=embedder,
    vector_store=vector_store,
    bm25_store=bm25_store,
    dense_weight=0.7,
    sparse_weight=0.3
)

# Retrieve
results = retriever.retrieve(query="Your question", top_k=5)
```

### Generation Strategies

#### Available Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| Groq | Groq API integration | Real-time applications |
| OpenAI | OpenAI API integration | Complex tasks |

#### Usage

```python
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import GenerationType
from groq import Groq

# Groq generation
groq_client = Groq(api_key="your_key")
generator = StrategyFactory.create_generator(
    GenerationType.GROQ,
    client=groq_client,
    model='llama-3.1-70b-versatile'
)

# OpenAI generation
import openai
openai_client = openai.OpenAI(api_key="your_key")
generator = StrategyFactory.create_generator(
    GenerationType.OPENAI,
    client=openai_client,
    model='gpt-4'
)

# Generate response
response = generator.generate(
    query="Your question",
    context="Retrieved context...",
    max_tokens=1024,
    temperature=0.7
)
```

### Evaluation Strategies

#### TRACe Evaluation

LLM-based evaluation that computes:
- **Relevance**: How relevant is the response to the query?
- **Utilization**: How well does the response use retrieved context?
- **Completeness**: How complete is the response?
- **Adherence**: Does the response follow instructions?

```python
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import EvaluationType
from groq import Groq

judge_client = Groq(api_key="your_key")
evaluator = StrategyFactory.create_evaluator(
    EvaluationType.TRACE,
    judge_client=judge_client,
    model='llama-3.3-70b-versatile'
)

# Evaluate
scores = evaluator.evaluate(
    query="Your question",
    retrieved_docs=results,
    response=response
)

print(f"Relevance: {scores['relevance_score']}")
print(f"Utilization: {scores['utilization_score']}")
print(f"Completeness: {scores['completeness_score']}")
print(f"Adherence: {scores['adherence_score']}")
```

---

## Complete Workflow Example

### End-to-End Pipeline

```python
import os
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer, CrossEncoder

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)

# ============================================================================
# STEP 1: Ingestion - Load and Parse Data
# ============================================================================
from ingestion import (
    RAGBenchCovidQALoader,
    ParserFactory,
    ParserType,
    DataProcessor
)

# Load dataset
loader = RAGBenchCovidQALoader(split="test", limit=100)
raw_data = loader.load()
print(f"Loaded {len(raw_data)} samples")

# Create parser
parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)

# Process into canonical Documents
processor = DataProcessor(parser_strategy=parser)
documents = processor.process_dataset(raw_data)
print(f"Processed {len(documents)} documents")

# ============================================================================
# STEP 2: RAG Pipeline - Chunk Documents
# ============================================================================
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import ChunkingType

chunker = StrategyFactory.create_chunker(
    ChunkingType.SENTENCE,
    max_words=100,
    overlap_sentences=1
)

all_chunks = []
for doc in documents:
    chunks = chunker.chunk(doc)
    all_chunks.extend(chunks)

print(f"Created {len(all_chunks)} chunks")

# ============================================================================
# STEP 3: RAG Pipeline - Generate Embeddings
# ============================================================================
from rag.config.enums import EmbeddingType

embedder = StrategyFactory.create_embedder(
    EmbeddingType.BGE,
    model='BAAI/bge-large-en-v1.5'
)

chunk_texts = [chunk.text for chunk in all_chunks]
embeddings = embedder.embed(chunk_texts)
print(f"Generated embeddings: {embeddings.shape}")

# ============================================================================
# STEP 4: RAG Pipeline - Build Vector Index
# ============================================================================
from rag.vectorstores.faiss_store import FaissVectorStore

vector_store = FaissVectorStore(dimension=embeddings.shape[1])
vector_store.add(embeddings, all_chunks)
print("Vector index built")

# ============================================================================
# STEP 5: RAG Pipeline - Setup Retrieval
# ============================================================================
from rag.config.enums import RetrievalType

reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')

retriever = StrategyFactory.create_retriever(
    RetrievalType.DENSE_RERANK,
    embedder=embedder,
    vector_store=vector_store,
    reranker=reranker,
    initial_k=20
)

# ============================================================================
# STEP 6: RAG Pipeline - Setup Generation
# ============================================================================
from rag.config.enums import GenerationType

generator = StrategyFactory.create_generator(
    GenerationType.GROQ,
    client=groq_client,
    model='llama-3.1-70b-versatile'
)

# ============================================================================
# STEP 7: RAG Pipeline - Setup Evaluation
# ============================================================================
from rag.config.enums import EvaluationType

evaluator = StrategyFactory.create_evaluator(
    EvaluationType.TRACE,
    judge_client=groq_client,
    model='llama-3.3-70b-versatile'
)

# ============================================================================
# STEP 8: Query Pipeline
# ============================================================================
query = "What is COVID-19?"

# Retrieve
retrieved_docs = retriever.retrieve(query, top_k=5)
print(f"Retrieved {len(retrieved_docs)} documents")

# Build context
context = "\n\n".join([
    f"Document {i+1}:\n{doc.text}"
    for i, doc in enumerate(retrieved_docs)
])

# Generate
response = generator.generate(
    query=query,
    context=context,
    max_tokens=1024,
    temperature=0.7
)
print(f"Response: {response}")

# Evaluate
scores = evaluator.evaluate(
    query=query,
    retrieved_docs=retrieved_docs,
    response=response
)
print(f"Evaluation Scores:")
print(f"  Relevance: {scores['relevance_score']:.4f}")
print(f"  Utilization: {scores['utilization_score']:.4f}")
print(f"  Completeness: {scores['completeness_score']:.4f}")
print(f"  Adherence: {scores['adherence_score']}")
```

### Using RAGPipeline (Simplified)

```python
from examples.complete_pipeline_example import RAGPipeline
from rag.config.loader import ConfigLoader
from rag.config.examples import config_high_quality

# Load configuration
config = config_high_quality

# Prepare clients
clients = {
    'groq': groq_client,
    'reranker': reranker
}

# Create pipeline
pipeline = RAGPipeline(config, clients)

# Build index
pipeline.build_index(documents)

# Query
result = pipeline.query("What is COVID-19?", top_k=5)

# Access results
print(f"Response: {result['response']}")
print(f"Scores: {result['scores']}")
```

---

## Configuration

### RAGConfig Structure

```python
from rag.config.config import RAGConfig
from rag.config.enums import (
    ChunkingType,
    EmbeddingType,
    RetrievalType,
    GenerationType,
    EvaluationType
)

config = RAGConfig(
    chunking=ChunkingConfig(
        type=ChunkingType.SENTENCE,
        max_words=100,
        overlap_sentences=1
    ),
    embedding=EmbeddingConfig(
        type=EmbeddingType.BGE,
        model_name='BAAI/bge-large-en-v1.5',
        dimension=1024
    ),
    vector_store=VectorStoreConfig(
        type=VectorStoreType.FAISS,
        dimension=1024
    ),
    retrieval=RetrievalConfig(
        type=RetrievalType.DENSE_RERANK,
        top_k=5,
        initial_k=20
    ),
    generation=GenerationConfig(
        type=GenerationType.GROQ,
        model='llama-3.1-70b-versatile',
        max_tokens=1024,
        temperature=0.7
    ),
    evaluation=EvaluationConfig(
        type=EvaluationType.TRACE,
        model='llama-3.3-70b-versatile'
    )
)
```

### Load from YAML

```python
from rag.config.loader import ConfigLoader

config = ConfigLoader.load('config/rag_config_high_quality.yaml')
```

### Pre-built Configurations

**fast_local** - Fast, no API calls
- Local embeddings (MiniLM, 384D)
- Dense retrieval
- Groq generation

**high_quality** - High quality with reranking
- Sentence-based chunking
- BGE embeddings (1024D)
- Dense + reranking retrieval
- Groq generation (70B)

**openai_production** - Production OpenAI setup
- Token-based chunking
- OpenAI embeddings (3072D)
- Hybrid retrieval
- GPT-4 generation

---

## Migration Guide

### From Old `data_loader` to New `ingestion`

#### OLD Approach (Deprecated)

```python
from data_loader import DataLoaderFactory, DataProcessor

# Load data
loader = DataLoaderFactory.create_covidqa_loader(split="test", limit=100)
raw_data = loader.load()

# Parse documents
parsed_docs = DataProcessor.process_dataset(raw_data)

# Convert to RAG documents
rag_docs = DataProcessor.convert_to_rag_documents(parsed_docs)
```

#### NEW Approach (Recommended)

```python
from ingestion import (
    RAGBenchCovidQALoader,
    ParserFactory,
    ParserType,
    DataProcessor
)

# Load data
loader = RAGBenchCovidQALoader(split="test", limit=100)
raw_data = loader.load()

# Create parser strategy
parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)

# Process into canonical Documents (no conversion needed)
processor = DataProcessor(parser_strategy=parser)
documents = processor.process_dataset(raw_data)
```

### Key Differences

| Aspect | OLD | NEW |
|--------|-----|-----|
| Package | `data_loader` | `ingestion` |
| Parser | `DocumentParser` (static methods) | `ParsingStrategy` (strategy pattern) |
| Output | `ParsedDocument` (intermediate) | `Document` (canonical) |
| Conversion | Manual `convert_to_rag_documents()` | Automatic (returns Document directly) |
| Extensibility | Hard to add new parsers | Easy (implement ParsingStrategy) |
| Separation | Mixed concerns | Clear separation (loaders/parsers/processors) |

### Benefits of Migration

1. **Cleaner Architecture**: Clear separation between loading, parsing, and processing
2. **Strategy Pattern**: Easy to add new parsers without modifying existing code
3. **Canonical Objects**: No intermediate conversion steps
4. **Better Testing**: Each component can be tested independently
5. **Future-Proof**: Ready for PDFs, Confluence, Slack, JSON, Markdown parsers

---

## Best Practices

### Ingestion Layer

1. **Use specific loaders when available**
   ```python
   # Good
   loader = RAGBenchCovidQALoader()
   
   # Also fine, but less specific
   loader = RAGBenchLoader(dataset_name="covidqa")
   ```

2. **Set limits for testing**
   ```python
   loader = RAGBenchCovidQALoader(limit=10)  # Quick test
   ```

3. **Enable caching for repeated loads**
   ```python
   config = DatasetLoadingConfig(use_cache=True)
   ```

4. **Use parser factory for extensibility**
   ```python
   parser = ParserFactory.create_parser(ParserType.TITLE_PASSAGE)
   ```

### RAG Pipeline

1. **Choose chunking strategy based on text type**
   - Natural text: Sentence chunking
   - Code/structured: Fixed window
   - API limits: Token chunking

2. **Use reranking for high precision**
   ```python
   retriever = StrategyFactory.create_retriever(
       RetrievalType.DENSE_RERANK,
       initial_k=20  # Retrieve more, rerank to top_k
   )
   ```

3. **Match embedding dimension to vector store**
   ```python
   embedder = StrategyFactory.create_embedder(
       EmbeddingType.BGE,
       model='BAAI/bge-large-en-v1.5'  # 1024D
   )
   vector_store = FaissVectorStore(dimension=1024)
   ```

4. **Use configuration files for reproducibility**
   ```python
   config = ConfigLoader.load('config/rag_config_high_quality.yaml')
   ```

5. **Evaluate your RAG system**
   ```python
   scores = evaluator.evaluate(query, retrieved_docs, response)
   ```

### Performance Tips

1. **Batch embedding generation**
   ```python
   # Good: Batch processing
   embeddings = embedder.embed(texts)
   
   # Avoid: One at a time
   for text in texts:
       embedding = embedder.embed([text])
   ```

2. **Use appropriate retrieval initial_k**
   ```python
   # For dense reranking
   initial_k = 20  # Retrieve 20, rerank to top_k=5
   ```

3. **Cache loaded data**
   ```python
   config = DatasetLoadingConfig(use_cache=True)
   ```

4. **Choose right chunk size**
   - Too small: Loss of context
   - Too large: Poor relevance
   - Sweet spot: 80-150 words for most use cases

---

## Extension Guide

### Adding a New Parser

```python
# 1. Create parser class
from ingestion.parsers.base import ParsingStrategy

class MarkdownParser(ParsingStrategy):
    def parse(self, raw_document, metadata=None):
        # Parse markdown
        title = extract_title(raw_document)
        content = extract_content(raw_document)
        
        from rag.models.document import Document
        return Document(
            title=title,
            content=content,
            metadata=metadata or {}
        )

# 2. Add to ParserType enum
from ingestion.parsers.strategy_factory import ParserType

class ParserType(str, Enum):
    TITLE_PASSAGE = "title_passage"
    MARKDOWN = "markdown"  # NEW

# 3. Register in factory
ParserFactory.register_parser(ParserType.MARKDOWN, MarkdownParser)

# 4. Use it
parser = ParserFactory.create_parser(ParserType.MARKDOWN)
```

### Adding a New Loader

```python
from ingestion.loaders.base import DatasetLoader, DatasetLoadingConfig

class LocalFileLoader(DatasetLoader):
    def __init__(self, file_path, config=None):
        super().__init__(config)
        self.file_path = file_path
    
    def load(self):
        # Load from local file
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        return data

# Use it
loader = LocalFileLoader('data/documents.json')
raw_data = loader.load()
```

### Adding a New Chunking Strategy

```python
from rag.chunking.base import ChunkingStrategy
from rag.models.chunk import Chunk

class CustomChunkingStrategy(ChunkingStrategy):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def chunk(self, document):
        # Custom chunking logic
        chunks = []
        # ... chunking implementation
        return chunks

# Register in factory
from rag.factory.strategy_factory import StrategyFactory
from rag.config.enums import ChunkingType

# Add to enum
class ChunkingType(str, Enum):
    SENTENCE = "sentence"
    CUSTOM = "custom"  # NEW

# Add to factory
StrategyFactory._CHUNKERS[ChunkingType.CUSTOM] = CustomChunkingStrategy

# Use it
chunker = StrategyFactory.create_chunker(ChunkingType.CUSTOM, param1=10, param2=20)
```

---

## Troubleshooting

### Common Issues

**Issue: Import error for datasets module**
- **Cause**: HuggingFace datasets not installed
- **Solution**: `pip install datasets`

**Issue: Parser returns empty title/content**
- **Cause**: Document format doesn't match expected pattern
- **Solution**: Check document format, use appropriate parser

**Issue: Embedding dimension mismatch**
- **Cause**: Vector store dimension doesn't match embedding dimension
- **Solution**: Ensure dimensions match when creating vector store

**Issue: Retrieval returns no results**
- **Cause**: Vector store empty or query embedding failed
- **Solution**: Verify vector store has data, check embedding generation

**Issue: Generation API rate limit**
- **Cause**: Too many API calls
- **Solution**: Implement rate limiting, use local models where possible

---

## Summary

This guide provides a complete reference for using the ingestion layer and RAG pipeline:

- **Ingestion Layer**: Load, parse, and preprocess data from various sources
- **RAG Pipeline**: Chunk, embed, retrieve, generate, and evaluate
- **Separation of Concerns**: Clear boundaries between ingestion and retrieval
- **Extensibility**: Easy to add new parsers, loaders, and strategies
- **Best Practices**: Performance tips and architectural guidelines

For specific implementation details, refer to the source code in:
- `ingestion/` - Ingestion layer implementation
- `rag/` - RAG pipeline implementation
- `examples/` - Working examples
- `config/` - Configuration files
