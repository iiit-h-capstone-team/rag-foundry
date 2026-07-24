# PubMedQA v11 Query Transform - Improvement Analysis

## Executive Summary

**Config:** `pubmedqa_title_aware_v11_query_transform`  
**Queries Analyzed:** 20  
**Overall Status:** Good retrieval, but generation needs refinement

### Key Metrics
| Metric | Predicted | Ground Truth | Deviation |
|--------|-----------|--------------|-----------|
| **Relevance** | 0.515 ± 0.262 | 0.489 ± 0.208 | 0.199 |
| **Utilization** | 0.299 ± 0.179 | 0.370 ± 0.240 | 0.162 |
| **Completeness** | 0.569 ± 0.277 | 0.685 ± 0.247 | 0.290 |
| **Adherence** | 0.250 ± 0.444 | 0.850 ± 0.366 | **0.600** ⚠️ |

---

## Critical Issues

### 1. **Adherence (CRITICAL)** - 12 queries failing
**Problem:** Generation is not sticking to retrieved passages; adding external knowledge or hedging.

**Affected Queries:**
- Q2: "Is diabetes mellitus a negative prognostic factor..." (pred=0.00, gt=1.00)
- Q3: "Do elderly persons need to be encouraged to drink more fluids?" (pred=0.00, gt=1.00)
- Q4: "Do the economic and social factors play..." (pred=0.00, gt=1.00)
- Q5: "Are prostate biopsies mandatory..." (pred=0.00, gt=1.00)
- Q6: "Do working conditions explain..." (pred=0.00, gt=1.00)
- Q17: "Are the statistical data from Benin's..." (pred=0.00, gt=1.00)
- Q18: "Association of chronic diseases..." (pred=0.00, gt=1.00)
- Q19: "Can metabolic disorders..." (pred=0.00, gt=1.00)
- Q9: "Can the Functional Movement Screen™..." (pred=0.00, gt=1.00)
- Q15: "Can we target smoking groups..." (pred=0.00, gt=1.00)
- Q16: "Going public: do risk and choice..." (pred=0.00, gt=1.00)
- Q20: "Association of chronic diseases..." (pred=0.00, gt=1.00)

**Root Cause:** System prompt allows hedging ("The provided context does not contain...") which violates adherence.

**Recommendation:**
```yaml
# In generation config, strengthen system prompt:
system_prompt: |
  You are a biomedical question answering assistant.
  Answer ONLY from the retrieved passages.
  Do NOT add information from your own knowledge.
  Do NOT hedge or say "the context does not contain."
  If passages don't answer the question, say: "The passages do not answer this question."
```

---

### 2. **Completeness (HIGH)** - 7 queries incomplete
**Problem:** Answers are too brief; missing relevant details from passages.

**Affected Queries:**
- Q17: "Are the statistical data from Benin's..." (pred=0.00, gt=1.00) - Missing all details
- Q19: "Can metabolic disorders..." (pred=0.25, gt=1.00) - Only partial answer
- Q4: "Do the economic and social factors..." (pred=0.71, gt=0.14) - Over-complete (verbose)
- Q18: "Association of chronic diseases..." (pred=1.00, gt=0.50) - Hallucinating
- Q15: "Can we target smoking groups..." (pred=0.56, gt=1.00) - Incomplete

**Root Cause:** Generation not extracting all relevant information from retrieved docs.

**Recommendation:**
- Increase `max_tokens` from 512 to 768
- Add to prompt: "Include all relevant findings, statistics, and details from the passages."
- Reduce `temperature` from 0.0 to 0.0 (already optimal)

---

### 3. **Utilization (MEDIUM)** - 11 queries underutilizing docs
**Problem:** Retrieved documents not being fully used in answers.

**Affected Queries:**
- Q17: util=0.000 (no docs used)
- Q1: util=0.125 (only 1 of 5 docs)
- Q7: util=0.125 (only 1 of 5 docs)
- Q2: util=0.154 (only 1 of 5 docs)
- Q5: util=0.167 (only 1 of 5 docs)

**Root Cause:** Generation focusing on first document only, ignoring others.

**Recommendation:**
- Reranker top_k is 7 but generation only sees first doc
- Check if context window is too small
- Increase context in retrieval config: `context_window: 2` (currently 1)

---

### 4. **Relevance (MEDIUM)** - 7 queries with low relevance
**Problem:** Retrieved documents not directly addressing the query.

**Affected Queries:**
- Q17: rel=0.100 (gt=0.167) - Wrong docs retrieved
- Q1: rel=0.125 (gt=0.500) - Partial match
- Q18: rel=0.182 (gt=0.667) - Off-topic docs
- Q6: rel=0.267 (gt=0.462) - Tangential match

**Root Cause:** Query transformation or retrieval not capturing query intent.

**Recommendation:**
- Check multi_query generation (num_queries=3)
- Verify query_transform is creating diverse queries
- Consider increasing top_k from 50 to 75 for better coverage

---

### 5. **Verbose Answers (LOW)** - 4 queries too long
**Problem:** Some answers exceed 150 words, violating conciseness.

**Affected Queries:**
- Q0: 198 words (adherence=1.00, acceptable)
- Q4: 157 words (adherence=0.00, problematic)
- Q9: 190 words (adherence=0.00, problematic)
- Q15: 159 words (adherence=0.00, problematic)

**Root Cause:** Generation not respecting conciseness requirement.

**Recommendation:**
- Add to prompt: "Be concise — limit answer to 100-120 words unless more detail is essential."
- Reduce `max_tokens` to 400 (currently 512)

---

## Retrieval Performance (✅ GOOD)

**Correct Documents Retrieved:** 20/20 (100%)
- All queries successfully retrieved their source documents
- No missing correct docs
- Ranking could be improved (some at rank 3-5 instead of rank 1)

---

## Configuration Recommendations

### Priority 1: Fix Adherence (Immediate)
```yaml
generation:
  config:
    system_prompt: |
      You are a biomedical question answering assistant.
      Answer ONLY from the retrieved passages below.
      Be concise but complete.
      Do NOT add information from your own knowledge.
      Do NOT hedge or say "the context does not contain."
      If the passages do not answer the question, say: "The passages do not answer this question."
    max_tokens: 400
    temperature: 0.0
```

### Priority 2: Improve Utilization (High)
```yaml
retrieval:
  search:
    searches:
      - type: dense
        config:
          top_k: 50
          context_window: 2  # Increase from 1 to include more context
      - type: sparse
        config:
          top_k: 50
  rerank:
    config:
      top_k: 10  # Increase from 7 to give generation more options
```

### Priority 3: Enhance Completeness (High)
```yaml
generation:
  config:
    max_tokens: 768  # Increase from 512
    user_prompt: |
      Passages:
      {context}

      Question: {query}

      Answer (from passages only, include all relevant findings and details):
```

### Priority 4: Improve Relevance (Medium)
```yaml
retrieval:
  query_transform:
    config:
      num_queries: 5  # Increase from 3 for better coverage
      temperature: 0.5  # Increase diversity
  search:
    searches:
      - type: dense
        config:
          top_k: 75  # Increase from 50
      - type: sparse
        config:
          top_k: 75
```

---

## Expected Improvements

With these changes:
- **Adherence:** 0.250 → 0.800+ (fix hedging in prompt)
- **Completeness:** 0.569 → 0.700+ (increase max_tokens, improve prompt)
- **Utilization:** 0.299 → 0.450+ (increase context_window, rerank top_k)
- **Relevance:** 0.515 → 0.600+ (more diverse queries, larger top_k)

---

## Testing Plan

1. Create `pubmedqa_v12_improved` config with above changes
2. Run on same 20 queries
3. Compare metrics against v11
4. Identify remaining issues
5. Iterate with targeted fixes

---

## Generated: 2026-07-18
**Analysis Tool:** `scripts/analyze_pubmedqa_report.py`
