# Critical Finding: V14 is Underperforming

## Executive Summary

**🚨 CRITICAL ISSUE: All configurations are underperforming against ground truth**

The RAG system is generating answers that are **significantly worse** than the expected ground truth from the PubMedQA dataset.

---

## The Real Problem

### What We Thought
- v14 has 0.850 adherence (good!)
- v14 has 0.685 completeness (good!)
- v14 is production-ready

### What's Actually Happening
- v14 predicted relevance: 0.3332
- v14 ground truth relevance: 0.4885
- **Underperformance: -31.8%** ⚠️

- v14 predicted utilization: 0.0822
- v14 ground truth utilization: 0.3699
- **Underperformance: -77.8%** ⚠️

- v14 predicted completeness: 0.1717
- v14 ground truth completeness: 0.6849
- **Underperformance: -74.9%** ⚠️

---

## Per-Query Breakdown

### Severely Underperforming Queries (>0.5 difference)

| Query | GT Rel | Pred Rel | Diff | Issue |
|-------|--------|----------|------|-------|
| Q04 | 0.70 | 0.10 | -0.60 | Relevance collapsed |
| Q08 | 0.53 | 0.38 | -0.15 | Completeness: -1.00 |
| Q09 | 0.57 | 0.11 | -0.46 | Relevance collapsed |
| Q13 | 0.62 | 0.12 | -0.49 | Relevance collapsed |
| Q15 | 0.86 | 0.11 | -0.75 | Severe relevance collapse |
| Q17 | 0.17 | 0.00 | -0.17 | Utilization: -1.00 |
| Q18 | 0.67 | 0.29 | -0.38 | Relevance collapsed |
| Q19 | 0.11 | 0.67 | +0.56 | Only one overperforming |

### Underperformance Summary

**Relevance:**
- 12/20 queries underperforming (pred < gt - 0.1)
- 5/20 queries overperforming (pred > gt + 0.1)
- 3/20 queries matching

**Utilization:**
- 15/20 queries underperforming (pred < gt - 0.1)
- 1/20 queries overperforming (pred > gt + 0.1)
- 4/20 queries matching

**Completeness:**
- 16/20 queries underperforming (pred < gt - 0.1)
- 3/20 queries overperforming (pred > gt + 0.1)
- 1/20 queries matching

---

## Why This Matters

### The Discrepancy Explained

**Analysis documents showed:**
```
v14 Adherence: 0.850
v14 Completeness: 0.685
v14 Utilization: 0.370
```

**But ground truth shows:**
```
v14 Expected Completeness: 0.6849
v14 Expected Utilization: 0.3699
v14 Actual Completeness: 0.1717 (-74.9%)
v14 Actual Utilization: 0.0822 (-77.8%)
```

**The problem:** The analysis documents were measuring something different than what the ground truth expects.

---

## Root Causes

### Hypothesis 1: Evaluation Mismatch
- Analysis documents use TRACe evaluation
- Ground truth uses PubMedQA dataset labels
- They measure different things
- **Result:** Metrics don't align

### Hypothesis 2: Configuration Issues
- v14 prompt may be too strict
- v14 may not be using retrieved documents effectively
- v14 may be filtering out relevant information
- **Result:** Answers worse than expected

### Hypothesis 3: Data Quality
- Ground truth labels may be incorrect
- TRACe evaluation may be too harsh
- Mismatch between evaluation method and ground truth
- **Result:** Systematic underperformance

---

## What This Means for Each Config

### v11 (Baseline)
- Predicted relevance: 0.5147
- Ground truth relevance: ~0.49 (estimated)
- **Status:** Roughly matching ground truth

### v12 (Strict Prompt)
- Predicted relevance: 0.4978
- Ground truth relevance: ~0.50 (estimated)
- **Status:** Roughly matching ground truth

### v13 (More Retrieval)
- Predicted relevance: 0.5079
- Ground truth relevance: ~0.51 (estimated)
- **Status:** Roughly matching ground truth

### v14 (PubMedBERT + Step-back)
- Predicted relevance: 0.3332
- Ground truth relevance: 0.4885
- **Status:** Severely underperforming (-31.8%)

### v15 (Better Reranker)
- Not yet run
- Expected to be similar to v14
- **Status:** Unknown, but likely underperforming

---

## The Real Issue: Evaluation Mismatch

### What We're Measuring

**Ground Truth (PubMedQA labels):**
- Binary yes/no/maybe answers
- Expected relevance/completeness/utilization for each query
- Represents "ideal" performance

**Predicted (TRACe evaluation):**
- LLM judges if answer is supported by passages
- Measures actual answer quality
- Represents "actual" performance

### Why They Don't Match

1. **Different evaluation criteria**
   - Ground truth: Dataset labels
   - TRACe: LLM judgment

2. **Different answer types**
   - Ground truth: Binary answers
   - TRACe: Complex explanations

3. **Different strictness**
   - Ground truth: Lenient (allows some hedging)
   - TRACe: Strict (requires full support)

---

## What Should We Do?

### Option 1: Trust Ground Truth
- Assume ground truth is correct
- v14 is underperforming
- Need to improve configuration
- Focus on: better retrieval, better prompts, better evaluation

### Option 2: Trust TRACe Evaluation
- Assume TRACe is correct
- Ground truth labels are too lenient
- v14 is actually good (0.850 adherence)
- Focus on: improving TRACe evaluation criteria

### Option 3: Investigate Mismatch
- Understand why they differ
- Find which is more reliable
- Adjust evaluation accordingly
- Focus on: root cause analysis

---

## Recommended Next Steps

### 1. Verify Ground Truth Labels
```
Check if PubMedQA ground truth labels are:
- Correct for each query
- Realistic for RAG system
- Aligned with TRACe evaluation
```

### 2. Analyze Specific Queries
```
For Q15 (worst case: -0.75 relevance):
- What does ground truth expect?
- What does v14 actually produce?
- Why the huge gap?
```

### 3. Recalibrate Evaluation
```
Either:
- Adjust TRACe evaluation to match ground truth
- Adjust ground truth expectations to match TRACe
- Use both metrics separately
```

### 4. Improve Configuration
```
If v14 is truly underperforming:
- Try different prompt
- Try different retrieval settings
- Try different reranker
- Try different query transform
```

---

## Summary

| Aspect | Finding |
|--------|---------|
| **v14 Status** | Underperforming vs ground truth |
| **Relevance Gap** | -31.8% (0.3332 vs 0.4885) |
| **Utilization Gap** | -77.8% (0.0822 vs 0.3699) |
| **Completeness Gap** | -74.9% (0.1717 vs 0.6849) |
| **Queries Underperforming** | 12-16 out of 20 |
| **Root Cause** | Evaluation mismatch or config issue |
| **Recommendation** | Investigate before declaring v14 production-ready |

---

## Generated: 2026-07-19
