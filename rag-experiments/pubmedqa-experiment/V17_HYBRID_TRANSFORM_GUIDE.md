# V17: Hybrid Transform Configuration

## Overview

**v17** is an aggressive improvement strategy designed to achieve better ground truth alignment while maintaining reasonable adherence.

**Base:** v14 (PubMedBERT + step-back)
**Strategy:** Hybrid query transform + aggressive retrieval
**Goal:** Relevance > 0.45, Utilization > 0.28, Completeness > 0.45

---

## Problem Statement

v14 and v16 still significantly underperform against ground truth:

| Metric | Ground Truth | v14 | v16 Revised | Gap |
|--------|--------------|-----|-------------|-----|
| **Relevance** | 0.4885 | 0.3332 | 0.40-0.45 | -4-9% |
| **Utilization** | 0.3699 | 0.0822 | 0.20-0.28 | -5-32% |
| **Completeness** | 0.6849 | 0.1717 | 0.35-0.45 | -20-34% |

**Root Causes:**
1. Query transform (step_back) may not generate enough query variations
2. Retrieval settings too conservative (top_k 75-85)
3. Reranker not keeping enough documents (top_k 15-20)
4. Answers still too short (600-700 tokens)

---

## Configuration Changes

### 1. Query Transform: step_back → multi_query (5 queries)

**Change:**
```yaml
# v14
query_transform:
  type: step_back

# v17
query_transform:
  type: multi_query
  config:
    num_queries: 5
    temperature: 0.3
```

**Rationale:**
- step_back: Breaks down complex queries (good for some)
- multi_query: Generates 5 alternative phrasings (better coverage)
- Temperature 0.3: Keeps queries on-topic but diverse
- **Why:** Better query coverage = more relevant documents

**Expected Impact:**
- +15-20% improvement in relevance
- Better handling of diverse query types

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

# v17
search:
  searches:
    - type: dense
      config:
        top_k: 100
```

**Rationale:**
- More candidates to choose from
- Reranker can pick best ones
- Minimal latency impact

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

# v17
search:
  searches:
    - type: sparse
      config:
        top_k: 100
```

**Rationale:**
- Keyword-based search complements dense search
- More candidates improve hybrid retrieval
- Sparse search is fast

**Expected Impact:**
- +3-5% improvement in relevance
- Better keyword matching

---

### 4. Min Similarity: 0.5 → 0.45

**Change:**
```yaml
# v14
search:
  searches:
    - type: dense
      config:
        min_similarity: 0.5

# v17
search:
  searches:
    - type: dense
      config:
        min_similarity: 0.45
```

**Rationale:**
- Slightly more lenient threshold
- Allows borderline relevant documents
- Reranker will filter out truly irrelevant ones
- Balance between coverage and quality

**Expected Impact:**
- +3-8% improvement in relevance
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

# v17
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 25
```

**Rationale:**
- Keep more documents in context
- Allows model to use more information
- 25 documents still fit in context window
- Improves completeness and utilization

**Expected Impact:**
- +10-15% improvement in completeness
- +15-20% improvement in utilization

---

### 6. Max Tokens: 600 → 750

**Change:**
```yaml
# v14
generation:
  config:
    max_tokens: 600

# v17
generation:
  config:
    max_tokens: 750
```

**Rationale:**
- Allows ~187-250 words
- Enough for comprehensive answers
- Still reasonable latency
- Balances completeness with speed

**Expected Impact:**
- +15-25% improvement in completeness
- +20-30% improvement in utilization

---

### 7. System Prompt: Strict + Thorough

**Change:**
```yaml
# v14
system_prompt: |
  Be concise but complete — include all relevant details.
  Aim for 100-150 words.

# v17
system_prompt: |
  CRITICAL RULES (MUST FOLLOW ALL):
  1. Answer ONLY from passages
  2. Include ALL relevant details
  3. Aim for 175-250 words
  4. Do NOT add hedging phrases
  5. Every claim must be traceable
  6. Do NOT add interpretations
```

**Rationale:**
- Explicit adherence rules
- Encourages comprehensive answers
- Prevents hallucination
- Maintains passage-only rule

**Expected Impact:**
- Maintains adherence (0.80-0.85)
- Improves completeness (+15-20%)

---

## Expected Results

### Predicted Improvements

| Metric | v14 | v17 Expected | Improvement | Status |
|--------|-----|--------------|-------------|--------|
| **Relevance** | 0.3332 | 0.43-0.50 | +29-50% | ✅ |
| **Utilization** | 0.0822 | 0.24-0.35 | +192-326% | ✅ |
| **Completeness** | 0.1717 | 0.40-0.50 | +133-191% | ✅ |
| **Adherence** | 0.850 | 0.80-0.85 | -0-5% | ⚠️ |

### Ground Truth Alignment

| Metric | Ground Truth | v14 Gap | v17 Gap | Improvement |
|--------|--------------|---------|---------|-------------|
| **Relevance** | 0.4885 | -0.1553 | -0.01 to -0.06 | +0.10-0.15 |
| **Utilization** | 0.3699 | -0.2878 | -0.02 to -0.13 | +0.16-0.27 |
| **Completeness** | 0.6849 | -0.5133 | -0.18 to -0.28 | +0.23-0.33 |
| **Adherence** | 0.850 | 0.000 | -0.00 to -0.05 | MAINTAINED |

---

## Comparison: v14 vs v16 vs v17

| Component | v14 | v16 Revised | v17 | Rationale |
|-----------|-----|-------------|-----|-----------|
| **Query Transform** | step_back | multi_query (5, 0.3T) | multi_query (5, 0.3T) | Same as v16 |
| **Dense top_k** | 75 | 85 | 100 | More aggressive |
| **Sparse top_k** | 75 | 85 | 100 | More aggressive |
| **Min Similarity** | 0.5 | 0.5 | 0.45 | Slightly relaxed |
| **Reranker top_k** | 15 | 20 | 25 | More aggressive |
| **Max Tokens** | 600 | 700 | 750 | More aggressive |
| **System Prompt** | Strict | Strict+Thorough | Strict+Thorough | Same as v16 |

**Philosophy:**
- v16: Conservative improvements (maintain adherence)
- v17: Aggressive improvements (better ground truth alignment)

---

## Risk Assessment

### Potential Issues

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Adherence drops below 0.80 | Medium | Strict prompt + lower temp |
| Latency increases | Low | Balanced top_k values |
| Hallucination increases | Medium | Strict prompt + evaluation |
| Still underperforms GT | Medium | Plan v18 with different embedding |

### Fallback Plan

**If adherence drops below 0.80:**
- Reduce max_tokens to 700
- Reduce reranker top_k to 20
- Reduce dense/sparse top_k to 90

**If relevance doesn't improve:**
- Try SciBERT embedding (v18)
- Try DeBERTa reranker (v18)

**If utilization still low:**
- Increase max_tokens to 800
- Increase reranker top_k to 30

---

## Testing Strategy

### Phase 1: Quick Test (5 queries)
```
Test on problem queries: Q01, Q03, Q04, Q09, Q15
Expected: Significant improvement in all metrics
Time: ~5 minutes
```

### Phase 2: Full Test (20 queries)
```
Run all queries
Compare against v14, v16, and ground truth
Time: ~10-15 minutes
```

### Phase 3: Analysis
```
Per-query breakdown
Identify regressions
Verify improvements
Time: ~5 minutes
```

---

## Success Criteria

### Minimum Success
- ✅ Relevance > 0.42 (vs v14's 0.3332)
- ✅ Utilization > 0.22 (vs v14's 0.0822)
- ✅ Completeness > 0.38 (vs v14's 0.1717)
- ✅ Adherence >= 0.80 (vs v14's 0.850)

### Target Success
- ✅ Relevance > 0.45 (vs GT 0.4885)
- ✅ Utilization > 0.28 (vs GT 0.3699)
- ✅ Completeness > 0.45 (vs GT 0.6849)
- ✅ Adherence >= 0.82 (vs v14's 0.850)

### Excellent Success
- ✅ Relevance > 0.48 (close to GT)
- ✅ Utilization > 0.32 (close to GT)
- ✅ Completeness > 0.50 (close to GT)
- ✅ Adherence >= 0.85 (maintain v14 level)

---

## Files

- **Config:** `config/pubmedqa_v17_hybrid_transform.yaml`
- **Guide:** `V17_HYBRID_TRANSFORM_GUIDE.md` (this file)
- **Design:** `scripts/design_v17_config.py`
- **Comparison:** `scripts/compare_v14_vs_v16.py` (can be adapted)

---

## Next Steps

1. **Create config file** ✅ (pubmedqa_v17_hybrid_transform.yaml)
2. **Run v17 on 5 problem queries**
3. **Compare against v14, v16, and ground truth**
4. **Run v17 on all 20 queries** (if promising)
5. **Generate comparison report**
6. **Plan v18** (if needed)

---

## Summary

**v17 is an aggressive improvement strategy:**

| Aspect | Approach |
|--------|----------|
| **Relevance** | Multi_query (5) + more retrieval (100) + relaxed threshold (0.45) |
| **Utilization** | More documents (25 reranker) + longer answers (750 tokens) |
| **Completeness** | More documents + longer answers + strict filtering |
| **Adherence** | Strict prompt + lower temp + evaluation |

**Expected outcome:**
- Relevance: +29-50% improvement
- Utilization: +192-326% improvement
- Completeness: +133-191% improvement
- Adherence: -0-5% (acceptable risk)

**Status:** Ready to test

---

## Generated: 2026-07-19
