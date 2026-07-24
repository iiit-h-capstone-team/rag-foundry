# V16: Improved Retrieval Configuration

## Overview

**v16** is designed to address the critical underperformance issues identified in v14.

**Base:** v14 (PubMedBERT + step-back)
**Goal:** Improve relevance, utilization, and completeness while maintaining adherence

---

## Problem Statement

v14 showed severe underperformance against ground truth:

| Metric | Ground Truth | v14 Predicted | Gap |
|--------|--------------|---------------|-----|
| Relevance | 0.4885 | 0.3332 | **-31.8%** |
| Utilization | 0.3699 | 0.0822 | **-77.8%** |
| Completeness | 0.6849 | 0.1717 | **-74.9%** |

**Root Causes:**
1. Answers not using retrieved documents effectively
2. Answers too short to cover all relevant information
3. Retrieved documents not relevant to query
4. Prompt too restrictive, discouraging document usage

---

## Configuration Changes

### 1. Query Transform: step_back → multi_query

**Change:**
```yaml
# v14
query_transform:
  type: step_back

# v16
query_transform:
  type: multi_query
  config:
    num_queries: 5
    temperature: 0.5
```

**Rationale:**
- step_back: Breaks down complex queries (good for some queries)
- multi_query: Generates alternative phrasings (good for coverage)
- **v16 uses multi_query:** Better for generating diverse query variations
- Generates 5 queries instead of 3 (v13 had 5, v14 had 1)
- Temperature 0.5 for some variation

**Expected Impact:**
- Better query coverage
- More relevant documents retrieved
- +10-15% improvement in relevance

**Note:** Could also try hybrid (step_back + multi_query) in future v17

---

### 2. Dense Search: top_k 75 → 100

**Change:**
```yaml
# v14
search:
  searches:
    - type: dense
      config:
        top_k: 75

# v16
search:
  searches:
    - type: dense
      config:
        top_k: 100
```

**Rationale:**
- More candidates to choose from
- Better chance of finding relevant documents
- Reranker can pick best ones from larger pool
- Minimal performance impact (still fast)

**Expected Impact:**
- +5-10% improvement in relevance
- Better coverage of document space

---

### 3. Sparse Search: top_k 75 → 100

**Change:**
```yaml
# v14
search:
  searches:
    - type: sparse
      config:
        top_k: 75

# v16
search:
  searches:
    - type: sparse
      config:
        top_k: 100
```

**Rationale:**
- Keyword-based search complements dense search
- More candidates improve hybrid retrieval
- Sparse search is fast, minimal latency impact

**Expected Impact:**
- +3-5% improvement in relevance
- Better keyword matching

---

### 4. Min Similarity: 0.5 → 0.4

**Change:**
```yaml
# v14
search:
  searches:
    - type: dense
      config:
        min_similarity: 0.5

# v16
search:
  searches:
    - type: dense
      config:
        min_similarity: 0.4
```

**Rationale:**
- v14 was too strict, filtering out borderline relevant docs
- 0.4 threshold is more lenient
- Allows documents with 40% semantic similarity
- Reranker will filter out truly irrelevant ones

**Expected Impact:**
- +5-10% improvement in relevance
- Better for low-resource queries

---

### 5. Reranker top_k: 15 → 25

**Change:**
```yaml
# v14
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 15

# v16
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 25
```

**Rationale:**
- Keep more documents in context window
- Allows model to use more information
- Improves completeness and utilization
- 25 documents still fit in context

**Expected Impact:**
- +10-15% improvement in completeness
- +15-20% improvement in utilization
- Better coverage of relevant information

---

### 6. Max Tokens: 600 → 800

**Change:**
```yaml
# v14
generation:
  config:
    max_tokens: 600

# v16
generation:
  config:
    max_tokens: 800
```

**Rationale:**
- v14 answers were too short
- 800 tokens allows ~200-300 words
- Enough space to cover all relevant information
- Still reasonable latency

**Expected Impact:**
- +20-30% improvement in completeness
- +30-40% improvement in utilization
- More comprehensive answers

---

### 7. System Prompt: Relaxed

**Change:**
```yaml
# v14
system_prompt: |
  Be concise but complete — include all relevant details from the passages.
  Aim for 100-150 words unless more detail is essential.

# v16
system_prompt: |
  Be thorough and comprehensive — aim for 200-300 words to cover all relevant aspects.
  Use multiple passages to build a comprehensive answer.
```

**Rationale:**
- v14 prompt discouraged longer answers
- v16 explicitly encourages comprehensive answers
- Still enforces passage-only rule
- Balances adherence with completeness

**Expected Impact:**
- +25-35% improvement in completeness
- +35-45% improvement in utilization
- Slight risk to adherence (0.850 → 0.80-0.85)

---

## Expected Results

### Predicted Improvements

| Metric | v14 | v16 Expected | Improvement |
|--------|-----|--------------|-------------|
| **Relevance** | 0.3332 | 0.42-0.48 | +26-44% |
| **Utilization** | 0.0822 | 0.25-0.35 | +204-326% |
| **Completeness** | 0.1717 | 0.45-0.55 | +162-220% |
| **Adherence** | 0.850 | 0.80-0.85 | -0-5% |

### Ground Truth Alignment

| Metric | Ground Truth | v16 Expected | Gap |
|--------|--------------|--------------|-----|
| **Relevance** | 0.4885 | 0.42-0.48 | -2-14% |
| **Utilization** | 0.3699 | 0.25-0.35 | -5-32% |
| **Completeness** | 0.6849 | 0.45-0.55 | -20-34% |

**Status:** Still underperforming, but significantly improved

---

## Implementation Details

### Configuration File
- **Path:** `config/pubmedqa_v16_improved_retrieval.yaml`
- **Base:** v14 configuration
- **Changes:** 7 modifications as outlined above

### Key Parameters

```yaml
# Query Transform
query_transform:
  type: multi_query
  num_queries: 5
  temperature: 0.5

# Search
dense_top_k: 100
sparse_top_k: 100
min_similarity: 0.4

# Reranking
reranker_top_k: 25

# Generation
max_tokens: 800
temperature: 0.0
```

---

## Testing Strategy

### Phase 1: Quick Test (5 queries)
```bash
# Test on problem queries
Q01, Q03, Q04, Q09, Q15
```

**Expected:** Significant improvement in utilization and completeness

### Phase 2: Full Test (20 queries)
```bash
# Run all queries
# Compare against v14 using ground truth
```

**Expected:** 
- Relevance: 0.42-0.48 (vs v14's 0.3332)
- Utilization: 0.25-0.35 (vs v14's 0.0822)
- Completeness: 0.45-0.55 (vs v14's 0.1717)

### Phase 3: Analysis
```bash
# Analyze per-query improvements
# Check for regressions
# Verify adherence maintained
```

---

## Risk Assessment

### Potential Issues

**1. Adherence Drop (0.850 → 0.80-0.85)**
- Longer answers may include hedging
- Mitigation: Keep strict prompt, monitor closely

**2. Latency Increase**
- More documents to process (100 vs 75)
- Longer generation (800 vs 600 tokens)
- Mitigation: Monitor and optimize if needed

**3. Hallucination Risk**
- Longer answers may add non-passage info
- Mitigation: Strict prompt + evaluation

**4. Still Underperforming**
- May not reach ground truth expectations
- Mitigation: Plan v17 with alternative approaches

---

## Alternative Approaches (if v16 doesn't work)

### Option A: Hybrid Query Transform (v17)
```yaml
query_transform:
  type: multi_query  # or step_back
  # Try both and see which works better
```

### Option B: Different Embedding (v17)
```yaml
embedding:
  model_name: allenai/scibert-base
  # or allenai/specter for better biomedical coverage
```

### Option C: Different Reranker (v17)
```yaml
rerank:
  model_name: sentence-transformers/nli-deberta-v3-large
  # or cross-encoder/qnli-distilroberta-base
```

### Option D: Query Expansion (v17)
```yaml
query_transform:
  type: query_rewriter
  # Rewrite queries to be more specific
```

---

## Success Criteria

### Minimum Success
- Relevance: > 0.40 (vs v14's 0.3332)
- Utilization: > 0.20 (vs v14's 0.0822)
- Completeness: > 0.40 (vs v14's 0.1717)
- Adherence: > 0.80 (vs v14's 0.850)

### Target Success
- Relevance: > 0.45 (vs ground truth's 0.4885)
- Utilization: > 0.30 (vs ground truth's 0.3699)
- Completeness: > 0.50 (vs ground truth's 0.6849)
- Adherence: > 0.80 (vs v14's 0.850)

### Excellent Success
- Relevance: > 0.48 (close to ground truth)
- Utilization: > 0.35 (close to ground truth)
- Completeness: > 0.55 (close to ground truth)
- Adherence: > 0.85 (maintain v14 level)

---

## Next Steps

1. **Create config file** ✅ (pubmedqa_v16_improved_retrieval.yaml)
2. **Run v16 on 5 problem queries** (Q01, Q03, Q04, Q09, Q15)
3. **Analyze results** (compare against v14 and ground truth)
4. **Run v16 on all 20 queries** (if promising)
5. **Generate comparison report** (v14 vs v16)
6. **Plan v17** (if v16 not sufficient)

---

## Summary

**v16 improves on v14 by:**
- Using multi_query for better query coverage
- Increasing retrieval top_k for more candidates
- Relaxing similarity threshold for borderline docs
- Keeping more documents in context (25 vs 15)
- Allowing longer answers (800 vs 600 tokens)
- Encouraging document usage in prompt

**Expected outcome:**
- Relevance: +26-44% improvement
- Utilization: +204-326% improvement
- Completeness: +162-220% improvement
- Adherence: -0-5% (slight risk)

**Status:** Ready to test

---

## Generated: 2026-07-19
