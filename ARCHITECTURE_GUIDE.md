# RAG Foundry Plugin Architecture Guide

**Status:** ✅ Complete and Verified  
**Date:** June 29, 2026  
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Principles](#architecture-principles)
3. [Core Components](#core-components)
4. [Implementation Pattern](#implementation-pattern)
5. [Reference Implementations](#reference-implementations)
   - [Chunking Module](#chunking-module-reference-implementation)
   - [Embedding Module](#embedding-module-reference-implementation)
   - [Generation Module](#generation-module-reference-implementation)
   - [Evaluation Module](#evaluation-module-reference-implementation)
   - [Reranking Module](#reranking-module-reference-implementation)
6. [How to Extend to Other Modules](#how-to-extend-to-other-modules)
7. [Usage Examples](#usage-examples)
8. [Verification](#verification)

---

## Overview

RAG Foundry uses a generic Registry + Strategy plugin architecture with class decorator-based registration. The core architecture is located at the **project root level** (`core/` folder) so it can be used by **any module** in the project, not just RAG modules.

### Key Features

- **Generic Base Classes:** `BaseStrategy[T]` and `BaseRegistry[T]` work with any module
- **Root-Level Core:** Core architecture at project root, available to all modules
- **Decorator-Based Registration:** Strategies register themselves using `@registry.register(key)`
- **Self-Contained Strategies:** Each strategy owns its configuration and implementation
- **Type-Safe:** No `Any` types for configs, full type hints throughout
- **Extensible:** Easy to add new strategies without modifying registry code
- **Lazy Loading:** Heavy dependencies loaded on demand

### Current Implementation

- **Core Architecture:** Located at `core/` (root level)
- **Chunking Module:** 4 strategies (Sentence, FixedWindow, Token, Semantic)
- **Embedding Module:** 7 strategies (SentenceTransformer, OpenAI, Ollama, Cohere, Voyage, HuggingFace, MedCPT)
- **Generation Module:** 1 strategy (Default - generates answers from context and query)
- **Evaluation Module:** 1 strategy (TRACe - LLM-based evaluation of answer quality)
- **Reranking Module:** 5 strategies (Cohere, Jina, CrossEncoder, MixedBread, Voyage - rerank documents by relevance)

---

## Architecture Principles

### 1. Plugin Architecture
- Strategies are plugins registered in a central registry
- New strategies can be added without modifying existing code
- Registry handles instantiation and lifecycle

### 2. Strategy Pattern
- Each strategy implements a common interface (extends `BaseStrategy`)
- Strategies are interchangeable
- Clients use registry to get strategies, not direct imports

### 3. Configuration Ownership
- Each strategy owns its configuration dataclass
- Configs inherit from `BaseStrategyConfig`
- Configs are coerced from dicts using `coerce_config()`

### 4. Decorator-Based Registration
- Strategies register themselves via `@registry.register(key)` decorator
- Decorator wraps class in factory function
- No central registration code needed

### 5. Lazy Loading
- Heavy dependencies imported only when needed
- Graceful degradation if dependencies unavailable
- Module imports fast even if some strategies unavailable

---

## Core Components

### BaseStrategy[T]

**Location:** `core/strategy.py`

```python
class BaseStrategy(Generic[T]):
    """Generic base class for all strategies.
    
    Stores configuration in __init__(config: T).
    Each strategy exposes domain-specific API.
    """
    
    def __init__(self, config: T):
        self.config = config
```

**Usage:**
```python
class MyStrategy(BaseStrategy):
    def __init__(self, config: MyConfig):
        super().__init__(config)
    
    def my_method(self):
        # Use self.config
        pass
```

### BaseRegistry[T]

**Location:** `core/registry.py`

```python
class BaseRegistry(Generic[T]):
    """Generic registry for plugin management.
    
    Methods:
    - register(key) - Decorator to register strategies
    - get(key) - Get strategy factory
    - create(key, **kwargs) - Create strategy instance
    - registered_keys() - List all registered keys
    """
    
    def register(self, key: Union[str, Enum]):
        """Decorator to register a strategy class.
        
        Wraps class in factory function automatically.
        Returns factory function (not class).
        """
        def decorator(strategy_class: Type[T]) -> Callable[..., T]:
            # Create factory function
            def factory(**kwargs) -> T:
                return strategy_class(**kwargs)
            
            # Store in registry
            self._strategies[normalized_key] = factory
            return factory
        return decorator
    
    def create(self, key: Union[str, Enum], **kwargs: Any) -> T:
        """Create strategy instance."""
        factory = self._strategies[normalized_key]
        return factory(**kwargs)
```

**Features:**
- Supports enum and string keys (auto-normalized)
- Meaningful error messages
- Type-safe instantiation
- Introspection via `registered_keys()`

### coerce_config()

**Location:** `core/config.py`

```python
def coerce_config(value: Any, config_cls: Type[T]) -> T:
    """Convert dict to dataclass or return existing instance.
    
    - If value is dict, instantiate config_cls with it
    - If value is already config_cls, return as-is
    - If value is None, instantiate with no args
    """
```

**Usage:**
```python
config = coerce_config({"model": "gpt-4"}, OpenAIConfig)
# Returns: OpenAIConfig(model="gpt-4")
```

---

## Implementation Pattern

### Step 1: Create Module Structure

```
rag/mymodule/
├── __init__.py              (imports + lazy loading)
├── base.py                  (MyStrategy extends BaseStrategy)
├── registry.py              (MyRegistry extends BaseRegistry)
├── enums.py                 (MyType enum)
├── config.py                (BaseMyConfig, MyConfig)
└── strategies/
    ├── strategy1/
    │   ├── __init__.py
    │   ├── config.py        (Strategy1Config)
    │   └── strategy.py      (@registry.register decorator)
    ├── strategy2/
    │   ├── __init__.py
    │   ├── config.py        (Strategy2Config)
    │   └── strategy.py      (@registry.register decorator)
    └── ...
```

### Step 2: Define Enums

**File:** `rag/mymodule/enums.py`

```python
from enum import Enum

class MyType(str, Enum):
    """Available strategies."""
    STRATEGY1 = "strategy1"
    STRATEGY2 = "strategy2"
    STRATEGY3 = "strategy3"
```

### Step 3: Define Base Config

**File:** `rag/mymodule/config.py`

```python
from dataclasses import dataclass
from typing import Any
from rag.mymodule.enums import MyType

@dataclass
class BaseMyConfig:
    """Base class for all strategy configs."""
    pass

@dataclass
class MyConfig:
    """Main config: which strategy plus its own typed config."""
    type: MyType
    config: Any = None

    def __post_init__(self):
        self.type = MyType(self.type)
        if self.config is None:
            self.config = {}
```

### Step 4: Define Base Strategy

**File:** `rag/mymodule/base.py`

```python
from abc import abstractmethod
from core.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    """Base class for my strategies.
    
    Defines the interface for implementations.
    """
    
    @abstractmethod
    def my_method(self):
        """Core method that all strategies implement."""
        pass
```

### Step 5: Define Registry

**File:** `rag/mymodule/registry.py`

```python
from core.registry import BaseRegistry
from rag.mymodule.base import MyStrategy

class MyRegistry(BaseRegistry[MyStrategy]):
    """Registry for my strategy plugins."""
    pass

my_registry = MyRegistry()
```

### Step 6: Create Strategy Configs

**File:** `rag/mymodule/strategies/strategy1/config.py`

```python
from dataclasses import dataclass
from rag.mymodule.config import BaseMyConfig

@dataclass
class Strategy1Config(BaseMyConfig):
    """Config for Strategy1."""
    param1: str = "default"
    param2: int = 10
```

### Step 7: Create Strategy Classes

**File:** `rag/mymodule/strategies/strategy1/strategy.py`

```python
from rag.mymodule.base import MyStrategy
from rag.mymodule.registry import my_registry
from rag.mymodule.enums import MyType
from rag.mymodule.strategies.strategy1.config import Strategy1Config

@my_registry.register(MyType.STRATEGY1)
class Strategy1(MyStrategy):
    """Implementation of Strategy1."""
    
    def __init__(self, config: Strategy1Config):
        super().__init__(config)
    
    def my_method(self):
        # Implementation using self.config
        pass
```

### Step 8: Module Initialization

**File:** `rag/mymodule/__init__.py`

```python
"""My module with registry-based strategy architecture."""

from rag.mymodule.base import MyStrategy
from rag.mymodule.registry import my_registry, MyRegistry
from rag.mymodule.enums import MyType
from rag.mymodule.config import MyConfig, BaseMyConfig

# Import all strategy configs
from rag.mymodule.strategies.strategy1.config import Strategy1Config
from rag.mymodule.strategies.strategy1.strategy import Strategy1

from rag.mymodule.strategies.strategy2.config import Strategy2Config
from rag.mymodule.strategies.strategy2.strategy import Strategy2

from rag.mymodule.strategies.strategy3.config import Strategy3Config

# Lazy imports for heavy dependencies
try:
    from rag.mymodule.strategies.strategy3.strategy import Strategy3 as _Strategy3
except ImportError:
    # Heavy dependency not available
    pass

# Lazy attribute access
def __getattr__(name):
    if name == "Strategy3":
        from rag.mymodule.strategies.strategy3.strategy import Strategy3
        return Strategy3
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "MyStrategy",
    "MyRegistry",
    "my_registry",
    "MyType",
    "MyConfig",
    "BaseMyConfig",
    "Strategy1Config",
    "Strategy1",
    "Strategy2Config",
    "Strategy2",
    "Strategy3Config",
]
```

---

## Chunking Module (Reference Implementation)

### Overview

The chunking module implements 4 strategies using the plugin architecture.

### Structure

```
rag/chunking/
├── base.py                  (ChunkingStrategy)
├── registry.py              (ChunkingRegistry + singleton)
├── enums.py                 (ChunkingType enum)
├── config.py                (BaseChunkingConfig, ChunkingConfig)
├── strategies/
│   ├── sentence/            (SentenceChunkingStrategy)
│   ├── fixed_window/        (FixedWindowChunkingStrategy)
│   ├── token/               (TokenChunkingStrategy)
│   └── semantic/            (SemanticChunkingStrategy)
└── __init__.py              (imports + lazy loading)
```

### Key Files

**Enums:** `rag/chunking/enums.py`
```python
class ChunkingType(str, Enum):
    SENTENCE = "sentence"
    FIXED_WINDOW = "fixed_window"
    TOKEN = "token"
    SEMANTIC = "semantic"
```

**Base Strategy:** `rag/chunking/base.py`
```python
class ChunkingStrategy(BaseStrategy):
    @abstractmethod
    def chunk(self, document: Document) -> List[Chunk]:
        pass
```

**Registry:** `rag/chunking/registry.py`
```python
class ChunkingRegistry(BaseRegistry[ChunkingStrategy]):
    pass

chunking_registry = ChunkingRegistry()
```

**Strategy Example:** `rag/chunking/strategies/sentence/strategy.py`
```python
@chunking_registry.register(ChunkingType.SENTENCE)
class SentenceChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: SentenceChunkingConfig):
        super().__init__(config)
    
    def chunk(self, document: Document) -> List[Chunk]:
        # Implementation
        pass
```

### Usage

```python
from rag.chunking import chunking_registry, ChunkingType, SentenceChunkingConfig

config = SentenceChunkingConfig(max_words=100)
chunker = chunking_registry.create(ChunkingType.SENTENCE, config=config)
chunks = chunker.chunk(document)
```

---

## Embedding Module (Reference Implementation)

### Overview

The embedding module implements 7 strategies using the plugin architecture.

### Structure

```
rag/embedding/
├── base.py                  (EmbeddingStrategy)
├── registry.py              (EmbeddingRegistry + singleton)
├── enums.py                 (EmbeddingType enum)
├── config.py                (BaseEmbeddingConfig, EmbeddingConfig)
├── strategies/
│   ├── sentence_transformer/
│   ├── openai/
│   ├── ollama/
│   ├── cohere/
│   ├── voyage/
│   ├── huggingface/
│   └── medcpt/
└── __init__.py              (imports + lazy loading)
```

### Key Files

**Enums:** `rag/embedding/enums.py`
```python
class EmbeddingType(str, Enum):
    SENTENCE_TRANSFORMER = "sentence_transformer"
    OPENAI = "openai"
    OLLAMA = "ollama"
    COHERE = "cohere"
    VOYAGE = "voyage"
    HUGGINGFACE = "huggingface"
    MEDCPT = "medcpt"
```

**Base Strategy:** `rag/embedding/base.py`
```python
class EmbeddingStrategy(BaseStrategy):
    @abstractmethod
    def embed(self, texts):
        pass
```

**Registry:** `rag/embedding/registry.py`
```python
class EmbeddingRegistry(BaseRegistry[EmbeddingStrategy]):
    pass

embedding_registry = EmbeddingRegistry()
```

**Strategy Example:** `rag/embedding/strategies/openai/strategy.py`
```python
@embedding_registry.register(EmbeddingType.OPENAI)
class OpenAIEmbeddingStrategy(EmbeddingStrategy):
    def __init__(self, config: OpenAIEmbeddingConfig):
        super().__init__(config)
    
    def embed(self, texts):
        # Implementation
        pass
```

### Usage

```python
from rag.embedding import embedding_registry, EmbeddingType, OpenAIEmbeddingConfig

config = OpenAIEmbeddingConfig(model="text-embedding-3-small")
embedder = embedding_registry.create(EmbeddingType.OPENAI, config=config)
embeddings = embedder.embed(texts)
```

---

## Generation Module (Reference Implementation)

### Overview

The generation module implements a single strategy that generates answers from retrieved documents and user queries. Providers (OpenAI, Ollama, Anthropic, etc.) are pluggable components used by the strategy.

### Structure

```
rag/generation/
├── base.py                  (GenerationStrategy)
├── registry.py              (GenerationRegistry + singleton)
├── enums.py                 (GenerationType enum)
├── config.py                (BaseGenerationConfig, GenerationConfig)
├── strategies/
│   └── default/
│       ├── __init__.py
│       ├── config.py        (DefaultGenerationConfig)
│       └── strategy.py      (@registry.register decorator)
└── __init__.py
```

### Key Files

**Enums:** `rag/generation/enums.py`
```python
class GenerationType(str, Enum):
    DEFAULT = "default"
```

**Base Strategy:** `rag/generation/base.py`
```python
class GenerationStrategy(BaseStrategy):
    @abstractmethod
    def generate(self, query: str, context: str) -> str:
        pass
```

**Registry:** `rag/generation/registry.py`
```python
class GenerationRegistry(BaseRegistry[GenerationStrategy]):
    pass

generation_registry = GenerationRegistry()
```

**Strategy Example:** `rag/generation/strategies/default/strategy.py`
```python
@generation_registry.register(GenerationType.DEFAULT)
class DefaultGenerationStrategy(GenerationStrategy):
    def __init__(self, config: DefaultGenerationConfig, provider):
        super().__init__(config)
        self.provider = provider
    
    def generate(self, query: str, context: str) -> str:
        # Build messages with system and user prompts
        # Call provider.generate()
        # Return response
```

### Usage

```python
from rag.generation import generation_registry, GenerationType, DefaultGenerationConfig

config = DefaultGenerationConfig(
    model="gpt-4",
    temperature=0.7,
    max_tokens=1000
)

# Provider is injected separately
strategy = generation_registry.create(
    GenerationType.DEFAULT,
    config=config,
    provider=openai_provider
)

answer = strategy.generate(query="What is AI?", context="...")
```

---

## Evaluation Module (Reference Implementation)

### Overview

The evaluation module implements a single strategy that evaluates the quality of generated answers using LLM-based evaluation. Providers (OpenAI, Ollama, Anthropic, etc.) are pluggable components used by the strategy.

### Structure

```
rag/evaluation/
├── base.py                  (EvaluationStrategy)
├── registry.py              (EvaluationRegistry + singleton)
├── enums.py                 (EvaluationType enum)
├── config.py                (BaseEvaluationConfig, EvaluationConfig)
├── strategies/
│   └── trace/
│       ├── __init__.py
│       ├── config.py        (TRACeEvaluationConfig)
│       └── strategy.py      (@registry.register decorator)
└── __init__.py
```

### Key Files

**Enums:** `rag/evaluation/enums.py`
```python
class EvaluationType(str, Enum):
    TRACE = "trace"
```

**Base Strategy:** `rag/evaluation/base.py`
```python
class EvaluationStrategy(BaseStrategy):
    @abstractmethod
    def evaluate(self, query: str, retrieved_docs, response: str) -> dict:
        pass
```

**Registry:** `rag/evaluation/registry.py`
```python
class EvaluationRegistry(BaseRegistry[EvaluationStrategy]):
    pass

evaluation_registry = EvaluationRegistry()
```

**Strategy Example:** `rag/evaluation/strategies/trace/strategy.py`
```python
@evaluation_registry.register(EvaluationType.TRACE)
class TRACeEvaluationStrategy(EvaluationStrategy):
    def __init__(self, config: TRACeEvaluationConfig, provider):
        super().__init__(config)
        self.provider = provider
    
    def evaluate(self, query: str, retrieved_docs, response: str) -> dict:
        # Build evaluation prompt
        # Call provider.generate()
        # Parse and return evaluation metrics
```

### Usage

```python
from rag.evaluation import evaluation_registry, EvaluationType, TRACeEvaluationConfig

config = TRACeEvaluationConfig(
    model="gpt-4",
    temperature=0.0,
    max_tokens=2000
)

# Provider is injected separately
strategy = evaluation_registry.create(
    EvaluationType.TRACE,
    config=config,
    provider=openai_provider
)

metrics = strategy.evaluate(
    query="What is AI?",
    retrieved_docs=[...],
    response="AI is..."
)
```

---

## Reranking Module (Reference Implementation)

### Overview

The reranking module implements strategies that rerank documents based on relevance to a query. Providers (Cohere, Jina, etc.) are pluggable components used by the strategies.

### Structure

```
rag/reranking/
├── base.py                  (RerankerStrategy)
├── registry.py              (RerankingRegistry + singleton)
├── enums.py                 (RerankingType enum)
├── config.py                (BaseRerankingConfig, RerankingConfig)
├── strategies/
│   ├── cohere/
│   │   ├── __init__.py
│   │   ├── config.py        (CohereRerankingConfig)
│   │   └── strategy.py      (@registry.register decorator)
│   ├── jina/
│   │   ├── __init__.py
│   │   ├── config.py        (JinaRerankingConfig)
│   │   └── strategy.py      (@registry.register decorator)
│   ├── cross_encoder/
│   │   ├── __init__.py
│   │   ├── config.py        (CrossEncoderRerankingConfig)
│   │   └── strategy.py      (@registry.register decorator)
│   ├── mixedbread/
│   │   ├── __init__.py
│   │   ├── config.py        (MixedBreadRerankingConfig)
│   │   └── strategy.py      (@registry.register decorator)
│   └── voyage/
│       ├── __init__.py
│       ├── config.py        (VoyageRerankingConfig)
│       └── strategy.py      (@registry.register decorator)
└── __init__.py
```

### Key Files

**Enums:** `rag/reranking/enums.py`
```python
class RerankingType(str, Enum):
    COHERE = "cohere"
    JINA = "jina"
    CROSS_ENCODER = "cross_encoder"
    MIXEDBREAD = "mixedbread"
    VOYAGE = "voyage"
```

**Base Strategy:** `rag/reranking/base.py`
```python
class RerankerStrategy(BaseStrategy):
    @abstractmethod
    def rerank(self, query, texts):
        pass
```

**Registry:** `rag/reranking/registry.py`
```python
class RerankingRegistry(BaseRegistry[RerankerStrategy]):
    pass

reranking_registry = RerankingRegistry()
```

**Strategy Example:** `rag/reranking/strategies/cohere/strategy.py`
```python
@reranking_registry.register(RerankingType.COHERE)
class CohereRerankingStrategy(RerankerStrategy):
    def __init__(self, config: CohereRerankingConfig, provider):
        super().__init__(config)
        self.provider = provider
    
    def rerank(self, query, texts):
        # Call provider.rerank()
        # Return reranked results
```

### Usage

```python
from rag.reranking import reranking_registry, RerankingType, CohereRerankingConfig

config = CohereRerankingConfig(
    model="rerank-english-v2.0",
    top_n=10
)

# Provider is injected separately
strategy = reranking_registry.create(
    RerankingType.COHERE,
    config=config,
    provider=cohere_provider
)

reranked_results = strategy.rerank(
    query="What is AI?",
    texts=[...]
)
```

---

## How to Extend to Other Modules

### Modules Already Refactored

✅ **Chunking Module** - 4 strategies  
✅ **Embedding Module** - 7 strategies  
✅ **Generation Module** - 1 strategy  
✅ **Evaluation Module** - 1 strategy  
✅ **Reranking Module** - 5 strategies  

### Modules Ready for Refactoring

The same architecture can be applied to:

1. **Retrieval Strategies** (`rag/retrieval/`)
2. **Search Strategies** (`rag/search/`)
3. **Fusion Strategies** (`rag/fusion/`)
4. **Query Transform Strategies** (`rag/query_transform/`)
5. **Vector Stores** (`rag/vectorstores/`)
6. **Dataset Loaders** (`rag/ingestion/loaders/`)

### Step-by-Step Refactoring Process

#### 1. Analyze Current Module

- Identify all strategy implementations
- List all configuration classes
- Identify common interface/base class
- Note any dependencies

#### 2. Create Module Structure

Follow the pattern from Chunking/Embedding modules:
- Create `base.py` with abstract base class
- Create `registry.py` with registry singleton
- Create `enums.py` with strategy type enum
- Create `config.py` with base and main configs
- Create `strategies/` folder with subfolders for each strategy

#### 3. Define Enums

```python
# rag/mymodule/enums.py
from enum import Enum

class MyType(str, Enum):
    STRATEGY1 = "strategy1"
    STRATEGY2 = "strategy2"
    # ... more strategies
```

#### 4. Define Configs

```python
# rag/mymodule/config.py
from dataclasses import dataclass
from rag.mymodule.enums import MyType

@dataclass
class BaseMyConfig:
    pass

@dataclass
class MyConfig:
    type: MyType
    config: Any = None
    
    def __post_init__(self):
        self.type = MyType(self.type)
        if self.config is None:
            self.config = {}

# rag/mymodule/strategies/strategy1/config.py
@dataclass
class Strategy1Config(BaseMyConfig):
    param1: str = "default"
```

#### 5. Define Base Strategy

```python
# rag/mymodule/base.py
from core.strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    @abstractmethod
    def my_method(self):
        pass
```

#### 6. Define Registry

```python
# rag/mymodule/registry.py
from core.registry import BaseRegistry
from rag.mymodule.base import MyStrategy

class MyRegistry(BaseRegistry[MyStrategy]):
    pass

my_registry = MyRegistry()
```

#### 7. Refactor Strategies

For each existing strategy:

```python
# rag/mymodule/strategies/strategy1/strategy.py
@my_registry.register(MyType.STRATEGY1)
class Strategy1(MyStrategy):
    def __init__(self, config: Strategy1Config):
        super().__init__(config)
    
    def my_method(self):
        # Existing implementation
        pass
```

#### 8. Update Module Initialization

```python
# rag/mymodule/__init__.py
from rag.mymodule.base import MyStrategy
from rag.mymodule.registry import my_registry, MyRegistry
from rag.mymodule.enums import MyType
from rag.mymodule.config import MyConfig, BaseMyConfig

# Import all strategies
from rag.mymodule.strategies.strategy1.config import Strategy1Config
from rag.mymodule.strategies.strategy1.strategy import Strategy1

# ... more imports

# Lazy imports for heavy dependencies
try:
    from rag.mymodule.strategies.heavy.strategy import HeavyStrategy as _HeavyStrategy
except ImportError:
    pass

def __getattr__(name):
    if name == "HeavyStrategy":
        from rag.mymodule.strategies.heavy.strategy import HeavyStrategy
        return HeavyStrategy
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "MyStrategy",
    "MyRegistry",
    "my_registry",
    "MyType",
    "MyConfig",
    "BaseMyConfig",
    # ... all configs and strategies
]
```

#### 9. Update Configuration Integration

If module configs are in `rag/config/config.py`:

```python
# rag/config/config.py
# Remove old configs and imports

# Update RAGConfig.from_dict() to import at runtime
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'RAGConfig':
    from rag.mymodule.config import MyConfig
    return cls(
        # ...
        mymodule=MyConfig(**data.get('mymodule', {})),
        # ...
    )
```

#### 10. Update Pipeline/Usage

Replace old factory usage with registry:

```python
# Before
from rag.mymodule.factory import MyFactory
strategy = MyFactory.create(config)

# After
from rag.mymodule import my_registry
strategy = my_registry.create(config.type, config=config.config)
```

#### 11. Verify

Create verification script following the pattern in `verify_all_phases.sh`:

```bash
# Test registry
python3 -c "
from rag.mymodule import my_registry, MyType
keys = my_registry.registered_keys()
print(f'Registry keys: {keys}')
"

# Test strategy creation
python3 -c "
from rag.mymodule import my_registry, MyType, Strategy1Config
config = Strategy1Config()
strategy = my_registry.create(MyType.STRATEGY1, config=config)
print(f'Created {type(strategy).__name__}')
"
```

---

## Usage Examples

### Creating a Strategy

```python
from rag.chunking import chunking_registry, ChunkingType, SentenceChunkingConfig

config = SentenceChunkingConfig(max_words=100, overlap_sentences=1)
chunker = chunking_registry.create(ChunkingType.SENTENCE, config=config)
chunks = chunker.chunk(document)
```

### Using String Keys

```python
# Both enum and string keys work
chunker1 = chunking_registry.create(ChunkingType.SENTENCE, config=config)
chunker2 = chunking_registry.create("sentence", config=config)
# Both are equivalent
```

### Checking Available Strategies

```python
from rag.chunking import chunking_registry

keys = chunking_registry.registered_keys()
print(keys)  # ['fixed_window', 'sentence', 'token']
```

### Adding a New Strategy

```python
# 1. Create config
@dataclass
class CustomChunkingConfig(BaseChunkingConfig):
    custom_param: str = "default"

# 2. Create strategy with decorator
@chunking_registry.register(ChunkingType.CUSTOM)
class CustomChunkingStrategy(ChunkingStrategy):
    def __init__(self, config: CustomChunkingConfig):
        super().__init__(config)
    
    def chunk(self, document: Document) -> List[Chunk]:
        # Implementation
        pass

# 3. Import in __init__.py
from rag.chunking.strategies.custom.strategy import CustomChunkingStrategy
```

---

## Verification

### Run All Tests

```bash
cd /Users/aditya.narayan/git-personal/rag-foundry
bash verify_all_phases.sh
```

### Expected Output

```
[PHASE 1: CORE ARCHITECTURE]
✓ BaseStrategy imported
✓ BaseRegistry imported
✓ coerce_config imported

[PHASE 2: CHUNKING MODULE]
✓ Chunking registry keys: ['fixed_window', 'sentence', 'token']
✓ All core chunking strategies registered

[PHASE 2: EMBEDDING MODULE]
✓ Embedding registry keys: ['cohere', 'huggingface', 'ollama', 'openai', 'voyage']
✓ All core embedding strategies registered

[PHASE 3: CLASS DECORATOR REGISTRATION]
✓ Created SentenceChunkingStrategy via registry
✓ Created OpenAIEmbeddingStrategy via registry
✓ String key support works for chunking
✓ String key support works for embedding

[CONFIGURATION INTEGRATION]
✓ All example configs load correctly

[PIPELINE INTEGRATION]
✓ Pipeline compiles successfully

[END-TO-END TEST]
✓ Chunking works: 1 chunks created
✓ Embedding config works correctly

✅ ALL PHASES COMPLETE AND VERIFIED
```

### Test Specific Module

```python
from rag.chunking import chunking_registry, ChunkingType, SentenceChunkingConfig

# Test registry
keys = chunking_registry.registered_keys()
assert 'sentence' in keys

# Test strategy creation
config = SentenceChunkingConfig()
chunker = chunking_registry.create(ChunkingType.SENTENCE, config=config)
assert chunker is not None

print("✓ All tests passed")
```

---

## Key Takeaways

### Architecture Benefits

✅ **Reusable:** Same pattern works for all modules  
✅ **Extensible:** Easy to add new strategies  
✅ **Maintainable:** Clear separation of concerns  
✅ **Type-Safe:** Full type hints, no `Any` types  
✅ **Flexible:** Supports enum and string keys  
✅ **Lazy:** Heavy dependencies loaded on demand  

### Implementation Checklist

- [ ] Create module structure (base, registry, enums, config)
- [ ] Define strategy enums
- [ ] Define base and main configs
- [ ] Define base strategy class
- [ ] Define registry singleton
- [ ] Create strategy folders and implementations
- [ ] Add class decorators to strategies
- [ ] Update module `__init__.py`
- [ ] Update configuration integration
- [ ] Update pipeline/usage code
- [ ] Create verification script
- [ ] Test all strategies
- [ ] Document new module

### Common Pitfalls to Avoid

❌ Don't forget `super().__init__(config)` in strategy `__init__`  
❌ Don't import strategies directly in client code  
❌ Don't modify registry after initialization  
❌ Don't use `Any` types for configs  
❌ Don't forget lazy imports for heavy dependencies  

---

## Query Transform Module (Reference Implementation)

### Overview

The query transform module implements 4 strategies for transforming user queries before retrieval.

### Structure

```
rag/query_transform/
├── base.py                  (QueryTransformStrategy)
├── registry.py              (QueryTransformRegistry + singleton)
├── enums.py                 (QueryTransformType enum)
├── config.py                (BaseQueryTransformConfig, QueryTransformConfig)
├── strategies/
│   ├── noop/                (NoOpQueryTransformStrategy)
│   ├── hyde/                (HyDEQueryTransformStrategy)
│   ├── multi_query/         (MultiQueryQueryTransformStrategy)
│   └── step_back/           (StepBackQueryTransformStrategy)
└── __init__.py
```

### Key Interface

```python
class QueryTransformStrategy(BaseStrategy):
    @abstractmethod
    def transform(self, query: str) -> QueryTransformResult:
        """Transform query into dense_queries and sparse_queries lists."""
        pass
```

---

## Search Module (Reference Implementation)

### Overview

The search module implements 2 strategies for searching documents.

### Structure

```
rag/search/
├── base.py                  (SearchStrategy)
├── registry.py              (SearchRegistry + singleton)
├── enums.py                 (SearchType enum)
├── config.py                (BaseSearchConfig, SearchStrategyConfig, SearchPipelineConfig)
├── strategies/
│   ├── dense/               (DenseSearchStrategy)
│   └── sparse/              (SparseSearchStrategy)
└── __init__.py
```

### Key Interface

```python
class SearchStrategy(BaseStrategy):
    @abstractmethod
    def search(self, queries: list[str]) -> list[dict]:
        """Search for documents matching queries."""
        pass
```

---

## Fusion Module (Reference Implementation)

### Overview

The fusion module implements 3 strategies for combining multiple search results.

### Structure

```
rag/fusion/
├── base.py                  (FusionStrategy)
├── registry.py              (FusionRegistry + singleton)
├── enums.py                 (FusionType enum)
├── config.py                (BaseFusionConfig, FusionConfig)
├── strategies/
│   ├── noop/                (NoOpFusionStrategy)
│   ├── rrf/                 (RRFFusionStrategy)
│   └── weighted_sum/        (WeightedSumFusionStrategy)
└── __init__.py
```

### Key Interface

```python
class FusionStrategy(BaseStrategy):
    @abstractmethod
    def fuse(self, search_results: list[list[dict]]) -> list[dict]:
        """Combine multiple search result lists into one."""
        pass
```

---

## Vector Store Module (Reference Implementation)

### Overview

The vector store module implements strategies for storing and searching embeddings.

### Structure

```
rag/vectorstore/
├── base.py                  (VectorStoreStrategy)
├── registry.py              (VectorStoreRegistry + singleton)
├── enums.py                 (VectorStoreType enum)
├── config.py                (BaseVectorStoreConfig, VectorStoreConfig)
├── strategies/
│   └── faiss/               (FaissVectorStoreStrategy)
└── __init__.py
```

### Key Interface

```python
class VectorStoreStrategy(BaseStrategy):
    @abstractmethod
    def add(self, embeddings, chunks): pass

    @abstractmethod
    def search(self, query_embedding, top_k): pass
```

---

## Pipeline Folder

All pipeline orchestration classes are now in `rag/pipeline/`:

```
rag/pipeline/
├── context.py               (RetrievalContext)
├── search_pipeline.py       (SearchPipeline - runs multiple search strategies)
├── retrieval_pipeline.py    (RetrievalPipeline - orchestrates all retrieval stages)
├── rag_pipeline.py          (RAGPipeline - complete RAG system)
└── __init__.py
```

### Retrieval Pipeline Flow

```
query → query_transform → search_pipeline → fusion → reranker → results
```

---

## Provider Module (Reference Implementation)

### Overview

The provider module implements strategies for different LLM providers (Groq, OpenAI, Anthropic, Google).

### Structure

```
providers/
├── base/
│   ├── strategy.py           (ProviderStrategy)
│   ├── key_state.py          (KeyState - existing)
│   ├── exceptions.py         (Exceptions - existing)
│   └── provider.py           (Legacy BaseLLMProvider - kept for compatibility)
├── groq/
│   └── groq_provider.py      (GroqProvider - now registered)
├── registry.py               (ProviderRegistry + singleton)
├── enums.py                  (ProviderType enum)
├── config.py                 (BaseProviderConfig, ProviderConfig)
├── provider_factory.py       (Updated to use registry)
├── provider_manager.py       (Existing - unchanged)
└── __init__.py
```

### Key Interface

```python
class ProviderStrategy(BaseStrategy):
    @abstractmethod
    def generate(self, model: str, messages: list, **kwargs):
        """Generate a response from the model."""
        pass

    @abstractmethod
    def health(self) -> dict:
        """Provider diagnostics and status."""
        pass
```

### Usage Example

```python
from providers import provider_registry, ProviderType
from providers.config import ProviderConfig

# Create provider config
config = ProviderConfig(
    type=ProviderType.GROQ,
    api_key_env="GROQ_API_KEY",
    params={"cooldown_seconds": 60}
)

# Create provider via registry
provider = provider_registry.create(
    ProviderType.GROQ,
    api_keys=["key1", "key2"],
    config=config,
    cooldown_seconds=60
)

# Use provider
response = provider.generate(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Hello"}]
)
```

---

## Project Directory Layout

```
rag-foundry/
├── core/                     # Base strategy + registry (universal plugin system)
├── providers/                # LLM providers (shared utility)
├── embedding/                # Embedding strategies (shared utility)
├── vectorstore/              # Vector store strategies (shared utility)
├── evaluation/               # Evaluation strategies + offline runner
├── parsers/                  # Document parsers (registry pattern)
├── datasets/                 # Data loaders + processors
│   ├── loaders/              # Dataset loading strategies (HuggingFace, etc.)
│   └── processors/           # Data processing orchestration
├── reporting/                # Report strategies (registry pattern)
├── rag/
│   ├── modules/              # Pipeline strategy modules
│   │   ├── chunking/         # 4 strategies (fixed_window, sentence, token, semantic)
│   │   ├── search/           # 2 strategies (dense, sparse)
│   │   ├── fusion/           # 3 strategies (noop, rrf, weighted_sum)
│   │   ├── query_transform/  # 4 strategies (noop, hyde, multi_query, step_back)
│   │   ├── reranking/        # 5 strategies (cross_encoder, cohere, voyage, jina, mixedbread)
│   │   └── generation/       # 1 strategy (default)
│   ├── pipeline/             # Pipeline orchestration (rag, retrieval, search)
│   ├── config/               # Configuration dataclasses + enums
│   ├── models/               # Data models (Document, Chunk, QueryResult)
│   ├── cache/                # Content-addressed caching
│   ├── persistence/          # JSONL writer
│   └── runtime/              # Runtime utilities
├── experiment/               # Experiment runner
└── config/                   # YAML experiment/pipeline configs
```

### Module Categories

| Category | Modules | Description |
|----------|---------|-------------|
| **Shared Utilities** | `core/`, `providers/`, `embedding/`, `vectorstore/` | Domain-agnostic, reusable by any pipeline type |
| **Benchmarking** | `evaluation/`, `reporting/` | Offline quality assessment and report generation |
| **Data Ingestion** | `parsers/`, `datasets/` | Data loading and document parsing |
| **Pipeline Modules** | `rag/modules/*` | RAG-specific strategy modules |
| **Infrastructure** | `rag/pipeline/`, `rag/config/`, `rag/models/`, `rag/cache/` | Pipeline orchestration and support |

---

## Parsers Module

### Structure
```
parsers/
├── __init__.py               # Module exports
├── enums.py                  # ParserType enum
├── base.py                   # ParsingStrategy (BaseStrategy)
├── registry.py               # ParserRegistry + parser_registry singleton
└── title_passage_parser.py   # @parser_registry.register(ParserType.TITLE_PASSAGE)
```

### Usage
```python
from parsers import parser_registry, ParserType

parser = parser_registry.create(ParserType.TITLE_PASSAGE)
document = parser.parse("Title: Foo\nPassage: Bar content")
```

---

## Datasets Module

### Structure
```
datasets/
├── __init__.py               # Module exports
├── loaders/
│   ├── enums.py              # LoaderType enum
│   ├── base.py               # DatasetLoader (BaseStrategy) + DatasetLoadingConfig
│   ├── registry.py           # LoaderRegistry + loader_registry singleton
│   └── huggingface_loader.py # @loader_registry.register(LoaderType.HUGGINGFACE)
└── processors/
    └── data_processor.py     # DataProcessor (uses ParsingStrategy)
```

### Usage
```python
from datasets.loaders import loader_registry, LoaderType, DatasetLoadingConfig

loader = loader_registry.create(
    LoaderType.HUGGINGFACE,
    dataset_name="squad",
    split="train",
    config=DatasetLoadingConfig(limit=100),
)
raw_data = loader.load()
```

---

## Reporting Module

### Structure
```
reporting/
├── __init__.py               # Module exports (lazy imports)
├── enums.py                  # ReportType enum
├── base.py                   # ReportStrategy (BaseStrategy), Report, ReportSection
├── registry.py               # ReportRegistry + report_registry singleton
├── detailed_report.py        # @report_registry.register(ReportType.DETAILED_QUERY)
└── report_generator.py       # ReportGenerator
```

### Usage
```python
from reporting import report_registry, ReportType

strategy = report_registry.create(ReportType.DETAILED_QUERY)
```

---

## Evaluation Module (Offline)

Evaluation is **decoupled from the RAG pipeline** and runs as an offline step.
The pipeline writes retrieval + generation results to JSONL; evaluation reads
those files, scores each record, and writes enriched JSONL with `predicted_scores`.

### Structure
```
evaluation/
├── __init__.py               # Module exports
├── enums.py                  # EvaluationType enum
├── base.py                   # EvaluationStrategy (BaseStrategy)
├── config.py                 # EvaluationConfig, BaseEvaluationConfig
├── registry.py               # EvaluationRegistry + evaluation_registry singleton
├── runner.py                 # EvaluationRunner (reads JSONL, scores offline)
└── strategies/
    └── trace/
        ├── config.py         # TRACeEvaluationConfig
        └── strategy.py       # @evaluation_registry.register(EvaluationType.TRACE)
```

### Experiment Flow
```
RAGPipeline.query()          → writes JSONL (query, docs, answer, ground_truth)
EvaluationRunner.evaluate()  → reads JSONL, scores, writes enriched JSONL
ReportGenerator.generate()   → reads enriched JSONL, produces report
```

### Usage
```python
from evaluation.runner import EvaluationRunner
from evaluation.config import EvaluationConfig

eval_config = EvaluationConfig(type="trace", provider="groq_evaluator")
runner = EvaluationRunner(eval_config)
runner.evaluate_jsonl("temp/results.jsonl")
```

---

## Summary

This architecture provides a clean, maintainable, and extensible plugin system for RAG Foundry. The pattern established by the Chunking and Embedding modules has been applied to all modules in the framework.

**Current Status:**
- ✅ Core architecture implemented
- ✅ Chunking module refactored (4 strategies) — `rag/modules/chunking/`
- ✅ Embedding module promoted to shared utility (7 strategies) — `embedding/`
- ✅ Reranking module refactored (5 strategies) — `rag/modules/reranking/`
- ✅ Generation module refactored (1 strategy) — `rag/modules/generation/`
- ✅ Query Transform module refactored (4 strategies) — `rag/modules/query_transform/`
- ✅ Search module refactored (2 strategies) — `rag/modules/search/`
- ✅ Fusion module refactored (3 strategies) — `rag/modules/fusion/`
- ✅ Vector Store promoted to shared utility (1 strategy) — `vectorstore/`
- ✅ Provider module refactored (1 strategy - Groq) — `providers/`
- ✅ **Parsers extracted to top-level** (1 strategy) — `parsers/`
- ✅ **Datasets module created** (1 loader strategy) — `datasets/`
- ✅ **Reporting refactored to registry** (1 strategy) — `reporting/`
- ✅ **Evaluation decoupled from pipeline** (offline runner) — `evaluation/`
- ✅ **rag/modules/ grouping** for pipeline strategies
- ✅ Pipelines consolidated into `rag/pipeline/`

**Architecture Benefits:**
- Consistent registry+decorator pattern across all modules
- Easy to add new strategies (providers, chunking, embedding, etc.)
- Clean separation of concerns (shared utilities vs pipeline modules)
- Evaluation runs offline — no rate-limiting conflicts with generation
- Type-safe configurations with lazy loading of heavy dependencies
- Standalone module interfaces ready for extension to non-RAG experiments
- Extensible for future providers (OpenAI, Anthropic, Google, etc.)

---

**Last Updated:** June 29, 2026  
**Status:** ✅ COMPLETE AND VERIFIED  
**Ready for Production:** Yes
