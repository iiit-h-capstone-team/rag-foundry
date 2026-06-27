# Provider Documentation

This document provides installation requirements, authentication details, configuration examples, and supported models for all embedding and reranking providers in the RAG framework.

---

## Embedding Providers

### SentenceTransformer

**Type:** `sentence_transformer`  
**Strategy:** `SentenceTransformerEmbeddingStrategy`  
**Deployment:** Local

#### Installation
```bash
pip install sentence-transformers
```

#### Authentication
No authentication required. Models are downloaded from HuggingFace Hub.

#### Configuration Example
```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: BAAI/bge-large-en-v1.5
    dimension: 1024
```

#### Supported Models
Any SentenceTransformer-compatible model, including:
- BAAI/bge-large-en-v1.5
- BAAI/bge-base-en-v1.5
- BAAI/bge-small-en-v1.5
- BAAI/bge-m3
- intfloat/e5-small-v2
- intfloat/e5-base-v2
- intfloat/e5-large-v2
- Alibaba-NLP/gte-large-en-v1.5
- Alibaba-NLP/gte-base-en-v1.5
- Snowflake/snowflake-arctic-embed-l-v2.0
- mixedbread-ai/mxbai-embed-large-v1
- sentence-transformers/all-mpnet-base-v2
- sentence-transformers/all-MiniLM-L6-v2
- hkunlp/instructor-xl
- FremyCompany/BioLORD-2023

#### Notes
- Models are cached locally after first download
- Uses the existing runtime model cache to avoid duplicate model loading
- Supports any model from the Sentence Transformers library

---

### OpenAI

**Type:** `openai`  
**Strategy:** `OpenAIEmbeddingStrategy`  
**Deployment:** API

#### Installation
```bash
pip install openai
```

#### Authentication
Set the `OPENAI_API_KEY` environment variable:
```bash
export OPENAI_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
embedding:
  type: openai
  config:
    model: text-embedding-3-small
    dimension: 1536
```

#### Supported Models
- text-embedding-3-small
- text-embedding-3-large

#### Notes
- Client is lazily initialized on first use
- Requires valid OpenAI API key with access to embedding models

---

### Ollama

**Type:** `ollama`  
**Strategy:** `OllamaEmbeddingStrategy`  
**Deployment:** Local

#### Installation
```bash
pip install ollama
```

#### Authentication
No authentication required. Requires Ollama to be running locally.

#### Setup
1. Install Ollama from https://ollama.ai
2. Start the Ollama server (default: http://localhost:11434)
3. Pull embedding models: `ollama pull nomic-embed-text`

#### Configuration Example
```yaml
embedding:
  type: ollama
  config:
    model_name: nomic-embed-text
    dimension: 768
    base_url: http://localhost:11434
```

#### Supported Models
Any Ollama embedding model, including:
- nomic-embed-text
- mxbai-embed-large
- bge-m3
- granite-embedding
- all-minilm

#### Notes
- Requires Ollama server to be running locally
- Client is lazily initialized on first use
- Supports custom base_url for remote Ollama instances

---

### Cohere

**Type:** `cohere`  
**Strategy:** `CohereEmbeddingStrategy`  
**Deployment:** API

#### Installation
```bash
pip install cohere
```

#### Authentication
Set the `COHERE_API_KEY` environment variable:
```bash
export COHERE_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
embedding:
  type: cohere
  config:
    model_name: embed-english-v3
    dimension: 1024
    input_type: search_document
```

#### Supported Models
- embed-v4
- embed-english-v3
- embed-multilingual-v3

#### Notes
- Client is lazily initialized on first use
- `input_type` can be: `search_document`, `search_query`, `classification`, or `clustering`
- Requires valid Cohere API key

---

### Voyage AI

**Type:** `voyage`  
**Strategy:** `VoyageEmbeddingStrategy`  
**Deployment:** API

#### Installation
```bash
pip install voyageai
```

#### Authentication
Set the `VOYAGE_API_KEY` environment variable:
```bash
export VOYAGE_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
embedding:
  type: voyage
  config:
    model_name: voyage-large-2
    dimension: 1024
    input_type: document
```

#### Supported Models
- voyage-large-2
- voyage-3
- voyage-code-3
- voyage-law
- voyage-finance

#### Notes
- Client is lazily initialized on first use
- `input_type` can be: `document`, `query`, or `null` (default)
- Requires valid Voyage AI API key

---

### HuggingFace Inference

**Type:** `huggingface`  
**Strategy:** `HuggingFaceEmbeddingStrategy`  
**Deployment:** API

#### Installation
```bash
pip install requests
```

#### Authentication
Set the `HUGGINGFACE_API_KEY` environment variable (optional but recommended for higher rate limits):
```bash
export HUGGINGFACE_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
embedding:
  type: huggingface
  config:
    model_name: sentence-transformers/all-MiniLM-L6-v2
    dimension: 384
    api_url: null
```

#### Supported Models
Any embedding model hosted on HuggingFace Inference API.

#### Notes
- Uses HuggingFace's hosted inference API
- API key is optional but recommended for better rate limits
- Custom `api_url` can be specified for custom endpoints
- Default API URL: `https://api-inference.huggingface.co/models/{model_name}`

---

### MedCPT

**Type:** `medcpt`  
**Strategy:** `MedCPTEmbeddingStrategy`  
**Deployment:** Local

#### Installation
```bash
pip install sentence-transformers
```

#### Authentication
No authentication required. Models are downloaded from HuggingFace Hub.

#### Configuration Example
```yaml
embedding:
  type: medcpt
  config:
    query_model_name: ncbi/MedCPT-Query-Encoder
    article_model_name: ncbi/MedCPT-Article-Encoder
    dimension: 768
```

#### Supported Models
- ncbi/MedCPT-Query-Encoder (for queries)
- ncbi/MedCPT-Article-Encoder (for documents)

#### Notes
- Specialized for biomedical text
- Uses separate encoders for queries and documents
- Provides `embed_query()` and `embed_documents()` methods for dual-encoder usage
- Reuses the existing SentenceTransformer model cache
- Best performance on biomedical literature and clinical notes

---

## Reranker Providers

### CrossEncoder

**Type:** `cross_encoder`  
**Strategy:** `CrossEncoderRerankerStrategy`  
**Deployment:** Local

#### Installation
```bash
pip install sentence-transformers
```

#### Authentication
No authentication required. Models are downloaded from HuggingFace Hub.

#### Configuration Example
```yaml
reranker:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
```

#### Supported Models
Any SentenceTransformer CrossEncoder model, including:
- BAAI/bge-reranker-v2-m3
- BAAI/bge-reranker-large
- BAAI/bge-reranker-base
- cross-encoder/ms-marco-MiniLM-L-6-v2
- cross-encoder/ms-marco-MiniLM-L-12-v2
- cross-encoder/ms-marco-electra-base

#### Notes
- Models are cached locally after first download
- Uses the existing runtime model cache to avoid duplicate model loading
- Returns relevance scores for each document

---

### Cohere

**Type:** `cohere`  
**Strategy:** `CohereRerankerStrategy`  
**Deployment:** API

#### Installation
```bash
pip install cohere
```

#### Authentication
Set the `COHERE_API_KEY` environment variable:
```bash
export COHERE_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
reranker:
  type: cohere
  config:
    model_name: rerank-v3.5
    top_n: 10
```

#### Supported Models
- rerank-v3.5

#### Notes
- Client is lazily initialized on first use
- `top_n` controls how many top results to return scores for
- Requires valid Cohere API key

---

### Voyage AI

**Type:** `voyage`  
**Strategy:** `VoyageRerankerStrategy`  
**Deployment:** API

#### Installation
```bash
pip install voyageai
```

#### Authentication
Set the `VOYAGE_API_KEY` environment variable:
```bash
export VOYAGE_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
reranker:
  type: voyage
  config:
    model_name: rerank-2
    top_k: 10
```

#### Supported Models
- rerank-2

#### Notes
- Client is lazily initialized on first use
- `top_k` controls how many top results to return scores for
- Requires valid Voyage AI API key

---

### Jina AI

**Type:** `jina`  
**Strategy:** `JinaRerankerStrategy`  
**Deployment:** API

#### Installation
```bash
pip install requests
```

#### Authentication
Set the `JINA_API_KEY` environment variable:
```bash
export JINA_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
reranker:
  type: jina
  config:
    model_name: jina-reranker-v2-base
    top_n: 10
```

#### Supported Models
- jina-reranker-v2-base
- jina-reranker-v2-base-multilingual

#### Notes
- Uses Jina's reranking API
- `top_n` controls how many top results to return scores for
- Requires valid Jina AI API key

---

### MixedBread AI

**Type:** `mixedbread`  
**Strategy:** `MixedBreadRerankerStrategy`  
**Deployment:** API

#### Installation
```bash
pip install requests
```

#### Authentication
Set the `MIXEDBREAD_API_KEY` environment variable:
```bash
export MIXEDBREAD_API_KEY=your_api_key_here
```

#### Configuration Example
```yaml
reranker:
  type: mixedbread
  config:
    model_name: mxbai-rerank-large-v1
    top_n: 10
```

#### Supported Models
- mxbai-rerank-large-v1

#### Notes
- Uses MixedBread's reranking API
- `top_n` controls how many top results to return scores for
- Requires valid MixedBread AI API key

---

## Compatibility Matrix

### Embedding Providers

| Provider              | Strategy                              | Local/API | Example Models                                         |
| --------------------- | ------------------------------------- | --------- | ------------------------------------------------------ |
| SentenceTransformer   | SentenceTransformerEmbeddingStrategy  | Local     | BGE, E5, GTE, Arctic, MPNet, Instructor, BioLORD       |
| OpenAI                | OpenAIEmbeddingStrategy               | API       | text-embedding-3-small, text-embedding-3-large         |
| Ollama                | OllamaEmbeddingStrategy               | Local     | nomic-embed-text, mxbai-embed-large, granite-embedding |
| Cohere                | CohereEmbeddingStrategy               | API       | embed-v4, embed-english-v3                             |
| Voyage                | VoyageEmbeddingStrategy               | API       | voyage-large-2, voyage-3                               |
| HuggingFace Inference | HuggingFaceEmbeddingStrategy | API       | Any supported hosted embedding model                   |
| MedCPT                | MedCPTEmbeddingStrategy               | Local     | Query Encoder, Article Encoder                         |

### Reranker Providers

| Provider     | Strategy                     | Local/API | Example Models                        |
| ------------ | ---------------------------- | --------- | ------------------------------------- |
| CrossEncoder | CrossEncoderRerankerStrategy | Local     | BGE Rerankers, MS MARCO CrossEncoders |
| Cohere       | CohereRerankerStrategy       | API       | rerank-v3.5                           |
| Voyage       | VoyageRerankerStrategy       | API       | rerank-2                              |
| Jina         | JinaRerankerStrategy         | API       | jina-reranker-v2-base                 |
| MixedBread   | MixedBreadRerankerStrategy   | API       | mxbai-rerank-large-v1                 |
