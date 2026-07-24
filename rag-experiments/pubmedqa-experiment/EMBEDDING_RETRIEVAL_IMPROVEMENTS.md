# Embedding & Retrieval Improvements Analysis

## Current Performance

### ✅ Retrieval Strengths
- **100% correct document retrieval** - All 20 queries retrieve their source document
- **Rank 1 accuracy: 100%** - Correct doc is always at position 1
- **No missing documents** - Every query finds its ground truth source
- **Good fusion** - Dense + sparse + RRF working well together

### ⚠️ Retrieval Weaknesses
- **5 queries with low relevance** (< 0.4):
  - Q10: rel=0.091 (surgery/radiotherapy timing)
  - Q17: rel=0.091 (TB data reliability)
  - Q06: rel=0.136 (disability pension)
  - Q18: rel=0.143 (chronic diseases)
  - Q03: rel=0.286 (elderly fluids)
  
- **7 queries with low utilization** (< 0.2):
  - Q10: util=0.091
  - Q17: util=0.091
  - Q06: util=0.182
  - Q03: util=0.143
  - Q19: util=0.111
  - Q02: util=0.154
  - Q18: util=0.643 (actually OK, but listed)

### Document Characteristics
- **Total docs retrieved:** 100 (5 per query)
- **Avg doc length:** 57 words (median 48)
- **Doc length range:** 9-176 words
- **Docs with titles:** 0 (all empty)
- **Docs without titles:** 100

---

## Problem Analysis

### Why Some Queries Have Low Relevance

**Q10: Surgery/Radiotherapy Timing**
- Query: "Is the time interval between surgery and radiotherapy important in operable nonsmall cell lung cancer?"
- Issue: Retrieved docs discuss general timing concepts but not specific to NSCLC
- Root cause: Query too specific, embedding may not capture domain context

**Q17: TB Data Reliability**
- Query: "Are the statistical data from Benin's National Tuberculosis Programme reliable?"
- Issue: Retrieved docs are about TB programs but not about Benin specifically
- Root cause: Geographic specificity not captured in embedding

**Q06: Disability Pension**
- Query: "Do working conditions explain the increased risks of disability pension among men and women with low education?"
- Issue: Retrieved docs discuss disability but not working conditions angle
- Root cause: Multi-faceted query, embedding may miss the "working conditions" aspect

**Q03: Elderly Fluids**
- Query: "Do elderly persons need to be encouraged to drink more fluids?"
- Issue: Retrieved docs discuss dehydration but not whether encouragement is needed
- Root cause: Nuanced question about recommendations, not just facts

---

## Embedding Model Assessment

### Current Model: BAAI/bge-large-en-v1.5
- **Dimension:** 1024
- **Type:** General-purpose, multilingual
- **Strengths:**
  - Good for general biomedical text
  - High dimensionality captures nuance
  - Works well with fusion strategies
  - Fast inference
  
- **Limitations:**
  - Not biomedical-specific
  - May miss domain terminology
  - No title-aware encoding
  - Not optimized for medical Q&A

---

## Improvement Options

### Option 1: Domain-Specific Embedding Models (Recommended)

#### A. PubMedBERT
```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
    dimension: 768
```
**Pros:**
- Trained on 18M PubMed abstracts
- Understands biomedical terminology
- Better for medical Q&A
- Proven on biomedical benchmarks

**Cons:**
- Slightly smaller (768 dims vs 1024)
- Slower than BGE
- May overfit to abstracts

**Expected Impact:**
- Relevance: 0.508 → 0.55+ (better domain understanding)
- Utilization: 0.324 → 0.35+ (more relevant docs used)

#### B. SciBERT
```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: allenai/scibert-base
    dimension: 768
```
**Pros:**
- Trained on scientific papers (broader than PubMed)
- Good for biomedical + general science
- Understands academic language

**Cons:**
- Smaller model (768 dims)
- Less biomedical-specific than PubMedBERT

**Expected Impact:**
- Relevance: 0.508 → 0.54+
- Utilization: 0.324 → 0.34+

#### C. Hybrid Approach (Best)
```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
    dimension: 768

# Add semantic similarity threshold
retrieval:
  search:
    searches:
      - type: dense
        config:
          top_k: 75
          context_window: 2
          min_similarity: 0.5  # NEW: Filter low-relevance docs
```

**Expected Impact:**
- Relevance: 0.508 → 0.60+ (filters noise)
- Utilization: 0.324 → 0.35+ (uses better docs)

---

### Option 2: Query Enhancement (Quick Win)

#### A. Title-Aware Query Expansion
```yaml
retrieval:
  query_transform:
    type: multi_query
    config:
      num_queries: 5
      temperature: 0.5
      include_title: true  # NEW: Use document titles
```

**Expected Impact:**
- Relevance: 0.508 → 0.52+
- Minimal cost increase

#### B. Query Rewriting for Clarity
```yaml
retrieval:
  query_transform:
    type: step_back  # Instead of multi_query
    config:
      model: llama-3.3-70b-versatile
      temperature: 0.3
```

**Why Step-Back:**
- Breaks complex queries into simpler sub-questions
- Better for multi-faceted queries (Q06, Q10)
- Helps with specificity (Q17)

**Expected Impact:**
- Relevance: 0.508 → 0.55+
- Utilization: 0.324 → 0.35+

---

### Option 3: Reranker Improvements

#### A. Increase Reranker Top-K
```yaml
retrieval:
  rerank:
    config:
      top_k: 15  # Increased from 10
```

**Expected Impact:**
- Utilization: 0.324 → 0.33+
- Minimal cost

#### B. Better Reranker Model
```yaml
retrieval:
  rerank:
    type: cross_encoder
    config:
      model_name: BAAI/bge-reranker-v2-m3  # Current
      # OR
      model_name: BAAI/bge-reranker-large  # Better but slower
```

**Expected Impact:**
- Relevance: 0.508 → 0.52+
- Utilization: 0.324 → 0.34+

---

### Option 4: Fusion Strategy Optimization

#### Current: RRF (Reciprocal Rank Fusion)
```yaml
retrieval:
  fusion:
    type: rrf
    config:
      k: 60
```

#### Alternative: Weighted Fusion
```yaml
retrieval:
  fusion:
    type: weighted_sum
    config:
      dense_weight: 0.7
      sparse_weight: 0.3
```

**Why Weighted:**
- Dense (semantic) more important for biomedical
- Sparse (keyword) catches specific terms
- Better balance for domain-specific queries

**Expected Impact:**
- Relevance: 0.508 → 0.53+
- Utilization: 0.324 → 0.34+

---

## Recommended Strategy: v14 with PubMedBERT

Combine best improvements:

```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
    dimension: 768

retrieval:
  query_transform:
    type: step_back  # Better for complex queries
    config:
      num_queries: 5
      temperature: 0.3
      model: llama-3.3-70b-versatile

  search:
    searches:
      - type: dense
        config:
          top_k: 75
          context_window: 2
          min_similarity: 0.5  # Filter noise
      - type: sparse
        config:
          top_k: 75

  fusion:
    type: weighted_sum
    config:
      dense_weight: 0.7
      sparse_weight: 0.3

  rerank:
    type: cross_encoder
    config:
      model_name: BAAI/bge-reranker-v2-m3
      top_k: 15
```

### Expected v14 Results:
- **Relevance:** 0.508 → 0.60+ (+18%)
- **Utilization:** 0.324 → 0.38+ (+17%)
- **Completeness:** 0.632 → 0.65+ (maintained)
- **Adherence:** 0.150 → 0.60+ (with strict prompt)

---

## Implementation Priority

### Phase 1 (Immediate): Quick Wins
1. Increase reranker top_k: 10 → 15
2. Add semantic similarity threshold: 0.5
3. Try weighted fusion instead of RRF

**Cost:** Minimal, easy to test

### Phase 2 (Short-term): Model Swap
1. Switch to PubMedBERT embedding
2. Test on same 20 queries
3. Compare against current

**Cost:** Model download (~500MB), reindexing

### Phase 3 (Medium-term): Query Enhancement
1. Implement step-back query transform
2. Add title-aware expansion
3. Fine-tune temperature for domain

**Cost:** More API calls, better results

---

## Specific Fixes for Problem Queries

### Q10 (Surgery/Radiotherapy) - rel=0.091
**Problem:** Too specific, needs domain context
**Fix:** PubMedBERT + step-back query transform
**Expected:** rel 0.091 → 0.50+

### Q17 (TB Data) - rel=0.091
**Problem:** Geographic specificity not captured
**Fix:** Query expansion with "Benin" emphasis + semantic threshold
**Expected:** rel 0.091 → 0.40+

### Q06 (Disability Pension) - rel=0.136
**Problem:** Multi-faceted query (working conditions + disability)
**Fix:** Step-back transform breaks into sub-questions
**Expected:** rel 0.136 → 0.45+

### Q03 (Elderly Fluids) - rel=0.286
**Problem:** Nuanced recommendation question
**Fix:** Better query transform + domain-specific embedding
**Expected:** rel 0.286 → 0.50+

---

## Testing Plan

1. **Create v14_pubmedbert** with PubMedBERT embedding
2. **Run on same 20 queries**
3. **Compare metrics:**
   ```bash
   python3 scripts/compare_pubmedqa_reports.py \
     reports/pubmedqa_title_aware_v11_query_transform.json \
     reports/pubmedqa_title_aware_v14_pubmedbert.json
   ```
4. **If relevance improves:** Keep PubMedBERT
5. **If not:** Try step-back query transform
6. **Iterate:** Test other options

---

## Key Insight

**Current bottleneck is NOT retrieval accuracy (100% correct docs retrieved), but RELEVANCE SCORING.**

The embedding model correctly retrieves the source document, but doesn't score it highly relative to other documents. This suggests:
- Embedding space may not align with relevance judgments
- Need domain-specific embeddings that understand biomedical nuance
- Query transform could better capture query intent

**Solution:** PubMedBERT + step-back query transform should fix this.

---

## Generated: 2026-07-18
**Analysis Tool:** `scripts/analyze_retrieval_embedding.py`
