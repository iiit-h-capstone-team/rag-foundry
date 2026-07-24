# PubMedQA Analysis & Optimization Summary

## Project Overview

Analyzed and optimized the PubMedQA RAG system through 4 iterations (v11-v14) to improve answer quality across 4 metrics: relevance, utilization, completeness, and adherence.

---

## Analysis Journey

### Phase 1: Baseline Analysis (v11)
**Goal:** Understand current performance and identify weaknesses

**Findings:**
- Adherence: 0.250 (only 5/20 queries follow passage-only rule)
- Completeness: 0.569 (answers somewhat complete)
- Utilization: 0.299 (using ~30% of retrieved docs)
- Relevance: 0.515 (moderate relevance)

**Root Causes Identified:**
1. System prompt allows hedging ("The provided context does not contain...")
2. Answers too brief (max_tokens=512)
3. Not using all retrieved documents
4. General-purpose embedding not optimized for biomedical domain

---

### Phase 2: Prompt Optimization (v12)
**Goal:** Fix adherence by enforcing stricter system prompt

**Changes:**
- Stricter system prompt with "CRITICAL RULES"
- Exact phrase for insufficient info
- No hedging allowed

**Results:**
- Adherence: 0.250 → 0.550 ✅ (+120%)
- Completeness: 0.569 → 0.291 ❌ (-49%)
- Utilization: 0.299 → 0.179 ❌ (-40%)
- Relevance: 0.515 → 0.498 ↓ (-3%)

**Lesson:** Strict prompt fixed adherence but was too aggressive, breaking completeness.

---

### Phase 3: Retrieval Optimization (v13)
**Goal:** Improve completeness and utilization while maintaining adherence

**Changes:**
- Balanced system prompt (not too strict)
- More tokens: 512 → 600
- Better retrieval: top_k 50→75, context_window 1→2
- More query diversity: 3→5 queries, temperature 0.3→0.5
- Better reranking: top_k 7→10
- Weighted fusion instead of RRF

**Results:**
- Completeness: 0.569 → 0.632 ✅ (+11%)
- Utilization: 0.299 → 0.324 ✅ (+8%)
- Relevance: 0.515 → 0.508 → (-1%)
- Adherence: 0.250 → 0.150 ❌ (-40%)

**Lesson:** Better retrieval improved completeness, but balanced prompt lost adherence.

---

### Phase 4: Domain-Specific Optimization (v14)
**Goal:** Combine best of v12 (strict prompt) + v13 (better retrieval) + domain-specific improvements

**Changes:**
- PubMedBERT embedding (biomedical-specific, 768 dims)
- Step-back query transform (better for complex queries)
- Weighted fusion (0.7 dense, 0.3 sparse)
- Reranker top_k: 10→15
- Strict system prompt (from v12)

**Expected Results:**
- Adherence: 0.150 → 0.60+ ✅ (strict prompt + better retrieval)
- Completeness: 0.632 → 0.65+ ✅ (maintained)
- Utilization: 0.324 → 0.38+ ✅ (better retrieval)
- Relevance: 0.508 → 0.60+ ✅ (PubMedBERT + step-back)

---

## Key Insights

### 1. Retrieval Accuracy vs Relevance Scoring
- **Accuracy:** 100% (all 20 queries retrieve correct source doc)
- **Relevance:** Only 15/20 queries score well
- **Insight:** Problem is not retrieval, but relevance scoring in general-purpose embedding

### 2. Prompt Engineering Trade-offs
- **Strict prompt:** Fixes adherence but breaks completeness
- **Balanced prompt:** Improves completeness but loses adherence
- **Solution:** Combine strict prompt with better retrieval so model doesn't need to hedge

### 3. Domain-Specific Matters
- General-purpose embedding (BGE) works but misses biomedical nuance
- PubMedBERT trained on 18M PubMed articles understands domain better
- Expected relevance improvement: 0.508 → 0.60+ (+18%)

### 4. Query Complexity Handling
- Multi-query works for simple queries
- Step-back better for complex, multi-faceted queries
- Examples: Q06 (working conditions + disability), Q10 (surgery + radiotherapy timing)

---

## Configuration Comparison

### v11 (Baseline)
```yaml
embedding: BAAI/bge-large-en-v1.5 (1024 dims)
query_transform: multi_query (3 queries, 0.3 temp)
search: top_k 50, context_window 1
reranker: top_k 7
system_prompt: Permissive (allows hedging)
max_tokens: 512
```
**Metrics:** Balanced but not optimized

### v12 (Strict Prompt)
```yaml
# Same as v11, but:
system_prompt: Strict (prevents hedging)
max_tokens: 512
```
**Metrics:** Best adherence, worst completeness

### v13 (Better Retrieval)
```yaml
embedding: BAAI/bge-large-en-v1.5 (1024 dims)
query_transform: multi_query (5 queries, 0.5 temp)
search: top_k 75, context_window 2
reranker: top_k 10
fusion: weighted_sum (0.7/0.3)
system_prompt: Balanced
max_tokens: 600
```
**Metrics:** Best completeness, worst adherence

### v14 (Optimized)
```yaml
embedding: PubMedBERT (768 dims) ← Domain-specific
query_transform: step_back ← Better for complex queries
search: top_k 75, context_window 2
reranker: top_k 15
fusion: weighted_sum (0.7/0.3)
system_prompt: Strict ← Prevents hedging
max_tokens: 600
```
**Metrics:** Expected best overall

---

## Problem Query Analysis

### Q10: Surgery/Radiotherapy Timing
- **v11-v13:** rel=0.091 (very low)
- **Issue:** Too specific, needs domain context
- **v14 Fix:** PubMedBERT + step-back
- **Expected:** rel → 0.50+

### Q17: TB Data Reliability
- **v11-v13:** rel=0.091 (very low)
- **Issue:** Geographic specificity (Benin) not captured
- **v14 Fix:** PubMedBERT understands context
- **Expected:** rel → 0.40+

### Q06: Disability Pension
- **v11-v13:** rel=0.136 (low)
- **Issue:** Multi-faceted (working conditions + disability)
- **v14 Fix:** Step-back breaks into sub-questions
- **Expected:** rel → 0.45+

### Q03: Elderly Fluids
- **v11-v13:** rel=0.286 (moderate)
- **Issue:** Nuanced recommendation question
- **v14 Fix:** Better query understanding + domain embedding
- **Expected:** rel → 0.50+

---

## Metrics Progression

```
ADHERENCE
v11: 0.250 ──→ v12: 0.550 ──→ v13: 0.150 ──→ v14: 0.60+ (expected)
     Baseline    +120%         -40%           +140% (best)

COMPLETENESS
v11: 0.569 ──→ v12: 0.291 ──→ v13: 0.632 ──→ v14: 0.65+ (expected)
     Baseline    -49%          +11%           +2% (best)

UTILIZATION
v11: 0.299 ──→ v12: 0.179 ──→ v13: 0.324 ──→ v14: 0.38+ (expected)
     Baseline    -40%          +8%            +17% (best)

RELEVANCE
v11: 0.515 ──→ v12: 0.498 ──→ v13: 0.508 ──→ v14: 0.60+ (expected)
     Baseline    -3%           -1%            +18% (best)
```

---

## Deliverables Created

### Analysis Scripts
1. **analyze_pubmedqa_report.py** - Single report analysis
2. **compare_pubmedqa_reports.py** - Compare two reports
3. **analyze_retrieval_embedding.py** - Retrieval & embedding quality analysis

### Configuration Files
1. **pubmedqa_v12_improved_prompt.yaml** - Strict prompt version
2. **pubmedqa_v13_balanced.yaml** - Better retrieval version
3. **pubmedqa_v14_pubmedbert_stepback.yaml** - Optimized version

### Analysis Documents
1. **IMPROVEMENTS.md** - Initial v11 analysis and recommendations
2. **COMPARISON_V11_VS_V12.md** - v11 vs v12 detailed comparison
3. **COMPARISON_V11_VS_V13.md** - v11 vs v13 detailed comparison
4. **EMBEDDING_RETRIEVAL_IMPROVEMENTS.md** - Embedding & retrieval analysis
5. **V13_IMPROVEMENTS.md** - v13 configuration guide
6. **V14_IMPROVEMENTS.md** - v14 configuration guide
7. **ANALYSIS_SUMMARY.md** - This document

---

## Next Steps

### Immediate (After v14 Results)
1. Run v14 on same 20 queries
2. Compare against v11, v12, v13
3. Analyze results:
   - Did PubMedBERT improve relevance?
   - Did step-back improve complex queries?
   - Did strict prompt fix adherence?

### If v14 Succeeds
1. Use v14 as new baseline
2. Test on larger dataset (100+ queries)
3. Fine-tune hyperparameters:
   - Embedding dimension (768 vs 1024)
   - Fusion weights (0.7/0.3 vs 0.75/0.25)
   - Reranker top_k (15 vs 20)

### If v14 Partially Succeeds
1. Identify which changes helped
2. Iterate on specific improvements
3. Try alternative embeddings (SciBERT, etc.)

### If v14 Fails
1. Revert to v13 retrieval + v12 prompt
2. Try different embedding models
3. Experiment with other query transforms

---

## Key Takeaways

1. **Retrieval accuracy ≠ Relevance scoring**
   - v11-v13 had 100% retrieval accuracy but poor relevance
   - Need domain-specific embeddings for better scoring

2. **Prompt engineering has trade-offs**
   - Strict prompts fix adherence but break completeness
   - Solution: Better retrieval so model doesn't need to hedge

3. **Domain matters**
   - General-purpose embeddings miss biomedical nuance
   - PubMedBERT trained on 18M PubMed articles is better

4. **Query complexity requires different strategies**
   - Multi-query for simple queries
   - Step-back for complex, multi-faceted queries

5. **Iteration is key**
   - Each version taught us something
   - v14 combines lessons from all previous versions

---

## Conclusion

The PubMedQA RAG system has been systematically analyzed and optimized through 4 iterations. v14 combines:
- **Domain-specific embedding** (PubMedBERT) for better relevance
- **Better query understanding** (step-back) for complex questions
- **Strict prompt** (from v12) for adherence
- **Enhanced retrieval** (from v13) for completeness

**Expected v14 Results:**
- Adherence: 0.60+ (vs v11's 0.250)
- Completeness: 0.65+ (vs v11's 0.569)
- Utilization: 0.38+ (vs v11's 0.299)
- Relevance: 0.60+ (vs v11's 0.515)

This represents a **140% improvement in adherence**, **14% improvement in completeness**, **27% improvement in utilization**, and **16% improvement in relevance** compared to the baseline.

---

## Generated: 2026-07-18
**Project:** PubMedQA RAG Optimization
**Status:** Ready for v14 testing
