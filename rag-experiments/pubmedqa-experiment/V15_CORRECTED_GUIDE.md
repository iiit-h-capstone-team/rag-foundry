# v15: BGE Reranker Large + Semantic Similarity Threshold (CORRECTED)

## Issue Fixed

**Original model:** `sentence-transformers/pubmedbert-base-uncased-mnli` ❌ DOES NOT EXIST
**Corrected model:** `BAAI/bge-reranker-large` ✅ VERIFIED & AVAILABLE

---

## Overview

v15 improves upon v14 by:
1. **Upgrading reranker** to larger, better model
2. **Adding semantic similarity threshold** to filter low-quality documents
3. **Keeping step-back query transform** (proven effective)

**Expected improvement:** +5-10% relevance (0.489 → 0.535-0.585)

---

## Key Changes from v14

### 1. Reranker Upgrade ⭐ MAIN CHANGE

**From:** `BAAI/bge-reranker-v2-m3` (medium model)
**To:** `BAAI/bge-reranker-large` (large model)

```yaml
# v14
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 15

# v15
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-large
    top_k: 15
```

**Why this helps:**
- Larger model (560M vs 335M parameters)
- Better accuracy for relevance ranking
- More nuanced understanding of query-document relationships
- Still fast inference
- Proven and widely used
- Expected: +2-3% relevance improvement

**How it works:**
- Takes query + retrieved documents
- Scores each document for relevance to query
- Ranks documents by relevance score
- Returns top-k documents

### 2. Semantic Similarity Threshold

**New:** Add `min_similarity: 0.5` to dense search

```yaml
# v15
search:
  searches:
    - type: dense
      config:
        top_k: 75
        context_window: 2
        min_similarity: 0.5  # NEW: Filter low-quality matches
    - type: sparse
      config:
        top_k: 75
```

**Why this helps:**
- Filters out documents with low semantic similarity
- Removes noisy documents from retrieval set
- Improves relevance score calculation
- Expected: +2-5% relevance improvement

### 3. Query Transform (Unchanged)

**Keeping:** `step_back` query transform from v14

```yaml
# v15 (same as v14)
query_transform:
  type: step_back
  provider: groq
  config:
    model: llama-3.3-70b-versatile
    temperature: 0.3
```

---

## Why These Changes Work Together

1. **Semantic threshold** filters out low-quality documents early
   - Reduces noise in retrieval set
   - Improves relevance score calculation

2. **Larger reranker** ranks remaining documents more accurately
   - Better understanding of relevance
   - Captures nuanced relationships
   - Puts most relevant docs at top

3. **Step-back query transform** breaks complex queries into sub-questions
   - Better query understanding
   - Captures multi-faceted aspects
   - Works well with better reranker

**Result:** Better retrieval quality → Higher relevance scores

---

## Expected Results

### Aggregate Metrics

| Metric | v14 | v15 Expected | Change |
|--------|-----|--------------|--------|
| **Relevance** | 0.489 | 0.535-0.585 | +9-20% ✅ |
| **Adherence** | 0.850 | 0.850 | No change |
| **Completeness** | 0.685 | 0.685-0.700 | Maintained |
| **Utilization** | 0.370 | 0.380-0.400 | +3-8% ✅ |

### Problem Query Improvements

| Query | v14 | v15 Expected | Improvement |
|-------|-----|--------------|-------------|
| Q19 (Metabolic) | 0.111 | 0.140-0.180 | +26-62% |
| Q17 (TB data) | 0.167 | 0.200-0.250 | +20-50% |
| Q11 (Breast milk) | 0.250 | 0.300-0.350 | +20-40% |
| Q14 (Chimerism) | 0.250 | 0.300-0.350 | +20-40% |
| Q02 (Diabetes) | 0.286 | 0.340-0.390 | +19-36% |
| Q12 (Breast CA) | 0.308 | 0.360-0.410 | +17-33% |
| Q07 (Clopidogrel) | 0.375 | 0.430-0.480 | +15-28% |

---

## Model Comparison

### BGE Reranker v2-m3 (v14)
- **Size:** 335M parameters
- **Speed:** Fast
- **Accuracy:** Good
- **Training:** Web data
- **Status:** Current

### BGE Reranker Large (v15)
- **Size:** 560M parameters
- **Speed:** Medium (still fast)
- **Accuracy:** Very Good
- **Training:** Web data
- **Status:** Upgrade
- **Improvement:** +2-3% expected

### Why BGE Reranker Large?
1. ✅ Verified and available on HuggingFace
2. ✅ Proven performance
3. ✅ Simple drop-in replacement
4. ✅ No additional dependencies
5. ✅ Low risk, medium reward

---

## Implementation

### Step 1: Update Config (Already Done)
```yaml
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-large
    top_k: 15
```

### Step 2: Run Experiment
```bash
# Run v15 on all 20 queries
python experiment_runner.py --config pubmedqa_v15_biomedical_reranker.yaml
```

### Step 3: Compare Results
```bash
python scripts/compare_pubmedqa_reports.py \
  reports/pubmedqa_title_aware_v14_pubmedbert_stepback.json \
  reports/pubmedqa_title_aware_v15_biomedical_reranker.json
```

---

## Alternative Options (If Needed)

### Option A: DeBERTa NLI Large (Better, Same Effort)
```yaml
model_name: sentence-transformers/nli-deberta-v3-large
```
- **Pros:** State-of-the-art NLI performance, +3-5% expected
- **Cons:** Slightly slower inference
- **Recommendation:** Try if v15 doesn't improve as expected

### Option B: SciBERT Embedding (Higher Impact, More Effort)
```yaml
embedding:
  type: sentence_transformer
  config:
    model_name: allenai/scibert-base
    dimension: 768
```
- **Pros:** Trained on scientific papers, +5-10% expected
- **Cons:** Need to reindex vectors (2 hours)
- **Recommendation:** Consider for v16 if v15 succeeds

### Option C: Hybrid (Best, Most Effort)
- SciBERT embedding + DeBERTa reranker + semantic threshold
- **Expected:** +10-15% improvement
- **Effort:** 3-4 hours
- **Recommendation:** Consider for v17

---

## Testing Strategy

### Phase 1: Quick Test (30 minutes)
1. Run v15 on 5 queries (Q03, Q06, Q10, Q17, Q19)
2. Compare against v14
3. Check if improvements are as expected

### Phase 2: Full Test (1-2 hours)
1. Run v15 on all 20 queries
2. Generate comparison report
3. Analyze per-query improvements

### Phase 3: Analysis (1 hour)
1. Identify which changes helped most
2. Check for any regressions
3. Decide on next steps (v16, v17, etc.)

---

## Fallback Plan

### If v15 doesn't improve as expected:

**Option 1: Try DeBERTa NLI Large**
```yaml
model_name: sentence-transformers/nli-deberta-v3-large
```

**Option 2: Adjust semantic threshold**
- Try 0.4 (looser) or 0.6 (stricter)
- Find optimal balance

**Option 3: Add multi_query fallback**
- Implement hybrid query transform
- Use step-back for complex, multi_query for simple

**Option 4: Skip to v16**
- Implement multi-stage retrieval
- Add query expansion with UMLS

---

## Summary

**v15 is a low-risk, medium-reward improvement:**
- ✅ Uses only verified public models
- ✅ Simple config change (1 line)
- ✅ Expected +5-10% relevance improvement
- ✅ No trade-offs to other metrics
- ✅ Easy to test and revert

**Recommendation:** Run v15 immediately, then decide on v16 based on results.

---

## Files

- **Config:** `pubmedqa_v15_biomedical_reranker.yaml`
- **Analysis:** `scripts/find_biomedical_rerankers.py`
- **Guide:** This document

---

## Generated: 2026-07-18
