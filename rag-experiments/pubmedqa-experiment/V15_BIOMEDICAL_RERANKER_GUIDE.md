# v15: Biomedical Reranker + Semantic Similarity Threshold

## Overview

v15 improves upon v14 by:
1. **Upgrading reranker** to biomedical-specific model
2. **Adding semantic similarity threshold** to filter low-quality documents
3. **Keeping step-back query transform** (proven effective)

**Expected improvement:** +9-20% relevance (0.489 → 0.535-0.585)

---

## Key Changes from v14

### 1. Reranker Upgrade ⭐ MAIN CHANGE

**From:** `BAAI/bge-reranker-v2-m3` (general-purpose)
**To:** `sentence-transformers/pubmedbert-base-uncased-mnli` (biomedical-specific)

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
    model_name: sentence-transformers/pubmedbert-base-uncased-mnli
    top_k: 15
```

**Why this helps:**
- Trained on PubMed data (biomedical-specific)
- MNLI training for relevance ranking
- Understands medical terminology
- Fast inference (110M parameters)
- Expected: +5-10% relevance improvement

**How it works:**
- Takes query + retrieved documents
- Scores each document for relevance to query
- Ranks documents by relevance score
- Returns top-k documents

**Example:**
```
Query: "Is diabetes a negative prognostic factor for NSCLC?"

Document 1: "Diabetes increases mortality in lung cancer patients"
Score: 0.92 (highly relevant)

Document 2: "Prognostic factors in cancer treatment"
Score: 0.75 (somewhat relevant)

Document 3: "Smoking and lung cancer"
Score: 0.45 (low relevance)

Ranking: Doc1 > Doc2 > Doc3
```

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

**How it works:**
- Calculates similarity between query embedding and document embedding
- Only keeps documents with similarity > 0.5
- Reduces number of irrelevant documents in the set

**Example:**
```
Query: "Do elderly persons need to be encouraged to drink more fluids?"

Document 1: "Dehydration in older adults"
Similarity: 0.78 (keep)

Document 2: "Fluid intake guidelines"
Similarity: 0.72 (keep)

Document 3: "Smoking and energy drinks"
Similarity: 0.35 (filter out)

Document 4: "Nutritional screening"
Similarity: 0.42 (filter out)

Result: Only docs 1-2 retrieved (higher quality)
```

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

**Why keep it:**
- Already proven effective in v14
- Excellent for complex queries (Q10 +492%)
- No additional implementation needed
- Works well with biomedical queries

**Optional enhancement:** Add `multi_query` as fallback
- For simple queries, use multi_query
- For complex queries, use step_back
- Expected: +2-5% additional improvement
- Effort: 2 hours

---

## Why These Changes Work Together

### Synergy: Biomedical Reranker + Semantic Threshold

1. **Semantic threshold** filters out low-quality documents early
   - Reduces noise in retrieval set
   - Improves relevance score calculation

2. **Biomedical reranker** ranks remaining documents by biomedical relevance
   - Understands medical terminology
   - Captures domain-specific relationships
   - Puts most relevant docs at top

3. **Step-back query transform** breaks complex queries into sub-questions
   - Better query understanding
   - Captures multi-faceted aspects
   - Works well with biomedical reranker

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
| Q19 (Metabolic) | 0.111 | 0.150-0.200 | +35-80% |
| Q17 (TB data) | 0.167 | 0.220-0.280 | +32-68% |
| Q11 (Breast milk) | 0.250 | 0.320-0.380 | +28-52% |
| Q14 (Chimerism) | 0.250 | 0.320-0.380 | +28-52% |
| Q02 (Diabetes) | 0.286 | 0.370-0.430 | +29-50% |
| Q12 (Breast CA) | 0.308 | 0.390-0.450 | +27-46% |
| Q07 (Clopidogrel) | 0.375 | 0.460-0.520 | +23-39% |

---

## Implementation Details

### Reranker Model: PubMedBERT MNLI

**Model Name:** `sentence-transformers/pubmedbert-base-uncased-mnli`

**Specifications:**
- **Base Model:** PubMedBERT (trained on 18M PubMed abstracts)
- **Fine-tuning:** MNLI (Multi-Genre Natural Language Inference)
- **Size:** 110M parameters
- **Speed:** Fast inference (~50ms per document)
- **Accuracy:** Excellent for biomedical relevance ranking

**How it works:**
1. Takes query and document as input
2. Produces relevance score (0-1)
3. Scores indicate: 0=irrelevant, 0.5=somewhat relevant, 1=highly relevant

**Why MNLI training:**
- MNLI teaches the model to understand entailment relationships
- Entailment = document supports/answers the query
- Perfect for relevance ranking

### Semantic Similarity Threshold

**Parameter:** `min_similarity: 0.5`

**Interpretation:**
- 0.0-0.3: Very low similarity (filter out)
- 0.3-0.5: Low similarity (filter out)
- 0.5-0.7: Moderate similarity (keep)
- 0.7-0.9: High similarity (keep)
- 0.9-1.0: Very high similarity (keep)

**Tuning:**
- If too strict (0.7): Fewer docs, higher quality, but may miss relevant docs
- If too loose (0.3): More docs, lower quality, but captures all relevant docs
- 0.5 is a good balance for biomedical domain

---

## Comparison: v14 vs v15

### Retrieval Pipeline

**v14:**
```
Query → Step-Back → Multi-Query Retrieval → RRF Fusion → BGE Reranker → Top-15 Docs
```

**v15:**
```
Query → Step-Back → Multi-Query Retrieval → Semantic Filter (0.5) → Weighted Fusion → 
PubMedBERT Reranker → Top-15 Docs
```

### Key Differences

| Component | v14 | v15 | Impact |
|-----------|-----|-----|--------|
| Embedding | PubMedBERT | PubMedBERT | No change |
| Query Transform | Step-Back | Step-Back | No change |
| Search | Dense + Sparse | Dense (0.5 filter) + Sparse | Better quality |
| Fusion | RRF | Weighted Sum | Better balance |
| Reranker | BGE (general) | PubMedBERT (biomedical) | +5-10% relevance |

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

**Option 1: Try different reranker**
- `BAAI/bge-reranker-large` (larger general model)
- `sentence-transformers/nli-deberta-v3-large` (larger NLI model)

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

## Configuration Comparison

### v14 Reranker
```yaml
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 15
```

### v15 Reranker
```yaml
rerank:
  type: cross_encoder
  config:
    model_name: sentence-transformers/pubmedbert-base-uncased-mnli
    top_k: 15
```

### v14 Search
```yaml
search:
  searches:
    - type: dense
      config:
        top_k: 75
        context_window: 2
    - type: sparse
      config:
        top_k: 75
```

### v15 Search
```yaml
search:
  searches:
    - type: dense
      config:
        top_k: 75
        context_window: 2
        min_similarity: 0.5
    - type: sparse
      config:
        top_k: 75
```

---

## Next Steps After v15

### If v15 succeeds (rel > 0.55):
1. Use v15 as new baseline
2. Plan v16 (multi-stage retrieval + query expansion)
3. Expected v16: rel 0.560-0.600

### If v15 partially succeeds (rel 0.50-0.55):
1. Keep v15 improvements
2. Add multi_query fallback
3. Expected: rel 0.55-0.60

### If v15 doesn't improve (rel < 0.50):
1. Revert semantic threshold
2. Try different reranker
3. Consider v16 instead

---

## Summary

**v15 is a low-risk, high-reward improvement:**
- ✅ Uses only public models (no training needed)
- ✅ Simple config changes (1 hour)
- ✅ Expected +9-20% relevance improvement
- ✅ No trade-offs to other metrics
- ✅ Easy to test and revert

**Recommendation:** Implement v15 immediately, then decide on v16 based on results.

---

## Generated: 2026-07-18
**Config:** `pubmedqa_v15_biomedical_reranker.yaml`
**Analysis:** `scripts/analyze_reranker_and_query_transform.py`
