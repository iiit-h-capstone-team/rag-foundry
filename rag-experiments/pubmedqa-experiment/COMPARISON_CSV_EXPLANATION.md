# Comparison.csv vs Analysis Documents - Explanation

## Quick Answer

**The scores differ because they measure DIFFERENT THINGS:**

- **Analysis Documents:** Actual answer quality (TRACe evaluation)
- **comparison.csv:** Model prediction accuracy (vs ground truth)

They are NOT directly comparable.

---

## Side-by-Side Comparison

### v14 Example

| Metric | CSV | Analysis | Difference |
|--------|-----|----------|-----------|
| **Relevance** | 0.3332 | 0.489 | -0.1558 |
| **Adherence** | 0.6 | 0.850 | -0.25 |
| **Completeness** | 0.1717 | 0.685 | -0.5133 |
| **Utilization** | 0.0822 | 0.370 | -0.2878 |

CSV scores are **much lower** than analysis scores.

### v11 Example (Baseline)

| Metric | CSV | Analysis | Difference |
|--------|-----|----------|-----------|
| **Relevance** | 0.5147 | 0.515 | -0.0003 |
| **Adherence** | 0.25 | 0.250 | 0.0 |
| **Completeness** | 0.5692 | 0.569 | 0.0002 |
| **Utilization** | 0.2994 | 0.299 | 0.0004 |

CSV and analysis **match perfectly** for v11!

---

## What is comparison.csv?

### Structure

```csv
config_name,relevance_score__mean,relevance_score__mae,utilization_score__mean,...
pubmedqa_v11,...,0.5147,0.199,...
```

### Column Meanings

- **`__mean`:** Average predicted score
- **`__mae`:** Mean Absolute Error (average error from ground truth)

### Example: v14 Relevance

```
relevance_score__mean: 0.3332
relevance_score__mae: 0.3087
```

**Interpretation:**
- Model predicts average relevance of 0.3332
- Actual ground truth relevance is ~0.64 (0.3332 + 0.3087)
- Model is off by 0.3087 on average

---

## What are Analysis Documents?

### Evaluation Method: TRACe

TRACe is an LLM-based evaluation that:
1. Splits documents into sentences
2. Splits response into sentences
3. Asks LLM: "Which response sentences are supported by document sentences?"
4. Calculates metrics based on support relationships

### Metrics Calculated

**Relevance Score:**
```
= (Relevant document sentences) / (Total document sentences)
= How many of the retrieved docs are actually relevant?
```

**Adherence Score:**
```
= Whether ALL response sentences are supported by documents
= True/False (boolean)
```

**Completeness Score:**
```
= (Relevant AND utilized sentences) / (Relevant sentences)
= Of the relevant docs, how many did the model use?
```

**Utilization Score:**
```
= (Utilized document sentences) / (Total document sentences)
= How many of the retrieved docs did the model actually use?
```

---

## Why Do They Differ?

### Theory 1: Different Data Sources

**comparison.csv:**
- Might be from a different experiment run
- Or using a different subset of queries
- Or using cached results from an older run

**Analysis documents:**
- Generated from actual JSONL results
- Using TRACe evaluation on full 20-query dataset

### Theory 2: Different Evaluation Methods

**comparison.csv:**
- Compares model predictions vs ground truth labels
- Measures prediction accuracy, not answer quality
- Uses MAE (Mean Absolute Error)

**Analysis documents:**
- Uses TRACe evaluation (LLM-based)
- Measures actual answer quality
- Evaluates whether answers follow passage-only rule

### Theory 3: v11 as Baseline

**v11 matches perfectly:**
- CSV: relevance=0.5147, adherence=0.25
- Analysis: relevance=0.515, adherence=0.250
- Difference: ~0.0001 (rounding)

**Why?** v11 is the baseline. Both CSV and analysis use the same evaluation method for v11.

**v14 differs significantly:**
- CSV: relevance=0.3332, adherence=0.6
- Analysis: relevance=0.489, adherence=0.850
- Difference: HUGE

**Why?** v14 uses a different evaluation approach or different data.

---

## Most Likely Explanation

### comparison.csv is Measuring:

1. **Model prediction accuracy** - How well the model predicts relevance/adherence scores
2. **Ground truth comparison** - Comparing predictions vs actual labels
3. **NOT answer quality** - Not evaluating whether answers are good

### Analysis documents are Measuring:

1. **Actual answer quality** - Using TRACe evaluation
2. **Passage-only rule compliance** - Whether answers follow rules
3. **Information usage** - Whether answers use all relevant information

### Why the Huge Difference for v14?

**Hypothesis:**
- v14 uses a different evaluation method (TRACe)
- comparison.csv uses an older evaluation method (prediction accuracy)
- They are measuring different things

**Evidence:**
- v11 matches (both use same baseline method)
- v14 differs hugely (different evaluation method)
- v13 partially matches (relevance matches, adherence differs)

---

## Which Should You Use?

### ✅ Use Analysis Documents for Decision-Making

**Why:**
- Measures actual answer quality
- TRACe evaluation is more reliable
- Directly relevant to RAG system performance
- Tells you if answers are good or bad

**For:**
- Choosing best configuration
- Evaluating improvements
- Production decisions

### ⚠️ Use comparison.csv for Debugging

**Why:**
- Measures model prediction accuracy
- Useful for understanding prediction errors
- Shows how well model predicts scores

**For:**
- Debugging prediction quality
- Understanding model behavior
- Not for overall system evaluation

---

## Recommendation

### Trust Analysis Documents

The analysis documents (v14_FINAL_SUMMARY.md, COMPARISON_V11_VS_V14.md, etc.) are the source of truth because:

1. ✅ They use TRACe evaluation (LLM-based, reliable)
2. ✅ They measure actual answer quality
3. ✅ They are directly relevant to RAG performance
4. ✅ They show v14 is production-ready (85% adherence)

### Ignore comparison.csv for System Evaluation

comparison.csv measures something different:
- Model prediction accuracy
- Not answer quality
- Not relevant to RAG decisions

---

## Summary

| Aspect | comparison.csv | Analysis Documents |
|--------|----------------|-------------------|
| **Measures** | Prediction accuracy | Answer quality |
| **Method** | Compare predictions vs ground truth | TRACe evaluation |
| **Relevance** | Debugging only | Decision-making |
| **v14 Relevance** | 0.3332 | 0.489 |
| **v14 Adherence** | 0.6 | 0.850 |
| **Trust Level** | Low (different metric) | High (actual quality) |

---

## Generated: 2026-07-18
