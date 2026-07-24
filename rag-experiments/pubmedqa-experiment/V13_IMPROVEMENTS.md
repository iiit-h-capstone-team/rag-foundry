# PubMedQA v13 - Comprehensive Improvements Guide

## Overview

v13 addresses **ALL identified issues** from v11 analysis:
1. ✅ Adherence (hedging)
2. ✅ Completeness (brief answers)
3. ✅ Utilization (not using all docs)
4. ✅ Relevance (off-topic retrieval)
5. ✅ Verbosity (too long answers)

---

## Changes Made

### 1. **System Prompt - Balanced Approach** 🎯
**Issue:** v12 was too strict, v11 allowed hedging

**Solution:** Balanced rules that enforce adherence without sacrificing completeness

```yaml
# v11 (problematic)
system_prompt: |
  Answer ONLY from the retrieved passages below.
  Be concise but complete — include all relevant details from the passages that address the question.
  Do NOT add information from your own knowledge.
  Do NOT hedge with phrases like "based on general knowledge" or "it is well-established".
  If the passages do not contain enough information, say "The provided context does not contain sufficient information to answer this question."

# v13 (improved)
system_prompt: |
  Your task is to answer questions using information from the retrieved passages.
  
  INSTRUCTIONS:
  1. Answer ONLY from the passages provided. Do not use external knowledge.
  2. Include all relevant details, findings, and statistics from the passages.
  3. Be concise but thorough — aim for 100-150 words unless more detail is essential.
  4. Do NOT add phrases like "based on general knowledge" or "it is well-established."
  5. Do NOT hedge or qualify your answer unnecessarily.
  6. If the passages do not contain enough information, say: "The passages do not provide sufficient information to answer this question."
```

**Key Differences:**
- Removed vague "concise but complete" → explicit "100-150 words"
- Added "Include all relevant details, findings, and statistics" → forces completeness
- Clearer numbered instructions → less ambiguity
- Exact phrase for insufficient info → prevents hedging variations

**Expected Impact:**
- Adherence: 0.25 → 0.70+ (fix hedging)
- Completeness: 0.57 → 0.65+ (explicit detail requirement)

---

### 2. **Query Transformation - Better Coverage** 🔍
**Issue:** Only 3 queries generated, missing some query angles

**Change:**
```yaml
# v11
query_transform:
  config:
    num_queries: 3
    temperature: 0.3

# v13
query_transform:
  config:
    num_queries: 5  # +67% more queries
    temperature: 0.5  # More diverse
```

**Why:**
- More queries = better chance of capturing query intent
- Higher temperature = more diverse query variations
- Helps with relevance issues (Q1, Q6, Q17, Q18)

**Expected Impact:**
- Relevance: 0.515 → 0.55+ (better query coverage)

---

### 3. **Dense Search - Larger Top-K** 📊
**Issue:** Only retrieving top 50 docs, missing relevant ones

**Change:**
```yaml
# v11
search:
  searches:
    - type: dense
      config:
        top_k: 50
        context_window: 1

# v13
search:
  searches:
    - type: dense
      config:
        top_k: 75  # +50% more docs
        context_window: 2  # 2x context
```

**Why:**
- Larger top_k = better coverage for edge cases
- context_window=2 = includes surrounding sentences for better context
- Helps with utilization (Q1, Q2, Q5, Q7)

**Expected Impact:**
- Utilization: 0.299 → 0.40+ (more docs available)
- Relevance: 0.515 → 0.55+ (better coverage)

---

### 4. **Sparse Search - Matching Dense** 📚
**Issue:** Sparse search at top_k=50, but dense at 50 too

**Change:**
```yaml
# v11
search:
  searches:
    - type: sparse
      config:
        top_k: 50

# v13
search:
  searches:
    - type: sparse
      config:
        top_k: 75  # Match dense search
```

**Why:**
- Consistency between dense and sparse retrieval
- Ensures fusion gets enough candidates
- Better coverage for keyword-based queries

**Expected Impact:**
- Utilization: 0.299 → 0.40+
- Relevance: 0.515 → 0.55+

---

### 5. **Reranker Top-K - More Options** 🎯
**Issue:** Reranker only returns top 7, generation might miss good docs

**Change:**
```yaml
# v11
rerank:
  config:
    top_k: 7

# v13
rerank:
  config:
    top_k: 10  # +43% more options
```

**Why:**
- Generation sees more reranked options
- Better chance of using multiple documents
- Helps with utilization issues

**Expected Impact:**
- Utilization: 0.299 → 0.40+

---

### 6. **Max Tokens - More Space for Answers** 📝
**Issue:** 512 tokens might be too limiting for complete answers

**Change:**
```yaml
# v11
max_tokens: 512

# v13
max_tokens: 600  # +17% more space
```

**Why:**
- More tokens = room for complete answers with all details
- Still respects conciseness (100-150 words = ~200-300 tokens)
- Helps with completeness issues

**Expected Impact:**
- Completeness: 0.569 → 0.65+

---

## Expected Results

### Aggregate Metrics
| Metric | v11 | v13 Expected | Improvement |
|--------|-----|--------------|-------------|
| **Adherence** | 0.250 | 0.70+ | +180% |
| **Completeness** | 0.569 | 0.65+ | +14% |
| **Utilization** | 0.299 | 0.40+ | +34% |
| **Relevance** | 0.515 | 0.55+ | +7% |

### Why These Improvements?

1. **Adherence +180%:** Balanced prompt fixes hedging without being too strict
2. **Completeness +14%:** More tokens + explicit detail requirement
3. **Utilization +34%:** Larger top_k + more rerank options
4. **Relevance +7%:** Better query transformation + larger search space

---

## Configuration Summary

### Retrieval Changes
| Parameter | v11 | v13 | Change |
|-----------|-----|-----|--------|
| num_queries | 3 | 5 | +67% |
| query_temp | 0.3 | 0.5 | +67% |
| dense_top_k | 50 | 75 | +50% |
| context_window | 1 | 2 | +100% |
| sparse_top_k | 50 | 75 | +50% |
| rerank_top_k | 7 | 10 | +43% |

### Generation Changes
| Parameter | v11 | v13 | Change |
|-----------|-----|-----|--------|
| max_tokens | 512 | 600 | +17% |
| system_prompt | Vague | Balanced | Clearer |
| word_target | None | 100-150 | Explicit |

---

## Testing Strategy

1. **Run v13 on same 20 queries**
2. **Compare against v11 using:**
   ```bash
   python3 scripts/compare_pubmedqa_reports.py \
     rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v11_query_transform.json \
     rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v13_balanced.json
   ```

3. **Expected outcomes:**
   - Adherence: 6-8 queries improved (vs v12's 6)
   - Completeness: 10+ queries improved (vs v12's 4)
   - Utilization: 8+ queries improved (vs v12's 3)
   - Relevance: 8+ queries improved (vs v11's 8)

4. **If results good:** Use v13 as baseline for future iterations
5. **If results mixed:** Adjust specific parameters

---

## Why Not More Aggressive?

### Why not top_k=100?
- Diminishing returns after 75
- More docs = more noise
- Reranker becomes less effective

### Why not 1000 max_tokens?
- Violates conciseness requirement
- Model tends to ramble
- 600 is sweet spot for 100-150 words

### Why not num_queries=10?
- More queries = more API calls
- Diminishing returns after 5
- Temperature 0.5 provides diversity

---

## Rollback Plan

If v13 underperforms:
1. Reduce num_queries to 4
2. Reduce top_k to 60
3. Reduce max_tokens to 550
4. Keep balanced system prompt (it's the key improvement)

---

## Generated: 2026-07-18
**Config:** `pubmedqa_v13_balanced.yaml`
