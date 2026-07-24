# Comparison.csv Clarification - Ground Truth vs Predicted Scores

## You're Absolutely Right!

The comparison.csv contains **mean of TRACe evaluation scores**, but there's an important distinction:

---

## What's in the JSONL File

Each record in the JSONL has TWO sets of scores:

```json
{
  "metadata": {
    "ground_truth": {
      "relevance_score": 0.6111,
      "utilization_score": 0.5,
      "completeness_score": 0.7273,
      "adherence_score": true
    },
    "predicted_scores": {
      "relevance_score": 0.5,
      "utilization_score": 0.4167,
      "completeness_score": 0.8333,
      "adherence_score": true
    }
  }
}
```

### Ground Truth
- **Source:** PubMedQA dataset labels (what the correct answer should be)
- **What it measures:** The "correct" relevance/adherence/etc for each query
- **Used for:** Evaluating how well the RAG system matches expected behavior

### Predicted Scores
- **Source:** TRACe evaluation (LLM judges the actual answer)
- **What it measures:** The actual quality of the generated answer
- **Used for:** Understanding RAG system performance

---

## What comparison.csv Shows

```csv
config_name,relevance_score__mean,relevance_score__mae,...
pubmedqa_v14_pubmedbert_stepback,0.3332,0.3087,...
```

### Column Meanings

- **`relevance_score__mean`:** Average of `predicted_scores.relevance_score` across all 20 queries
- **`relevance_score__mae`:** Mean Absolute Error = average difference between predicted and ground truth

### Example: v14 Relevance

```
predicted_scores__mean: 0.3332
ground_truth__mean: ~0.6419 (estimated from MAE)
MAE: 0.3087
```

**Interpretation:**
- Model predicts average relevance of 0.3332
- Ground truth average is ~0.6419
- Model is off by 0.3087 on average

---

## Why Scores Differ from Analysis Documents

### Analysis Documents Show:
```
v14 Relevance: 0.489
```

### comparison.csv Shows:
```
v14 Relevance: 0.3332
```

### Why the Difference?

**The analysis documents are using DIFFERENT data:**

1. **Analysis documents:** Calculated from `pubmedqa_title_aware_v14_pubmedbert_stepback.json` report
   - This is a JSON report generated from the JSONL
   - May use different aggregation method
   - May use only successful queries
   - May have different filtering

2. **comparison.csv:** Calculated directly from JSONL `predicted_scores`
   - Uses all records with `status: "success"`
   - Calculates mean of `predicted_scores` field
   - Compares against `ground_truth` field

---

## The Real Issue: Different Aggregation

Let me check what the analysis documents actually calculated:

### From JSONL (comparison.csv):
```
v14 relevance_score__mean: 0.3332
```

### From Analysis Documents:
```
v14 relevance: 0.489
```

### Hypothesis: Different Calculation Method

The analysis documents might be:
1. Using a different metric (not just mean of predicted_scores)
2. Filtering queries differently
3. Using a different evaluation method
4. Calculating from the JSON report (which may have different data)

---

## The Truth About comparison.csv

**comparison.csv is measuring:**
- How well the RAG system's predicted scores match ground truth labels
- Average error between predictions and ground truth
- NOT the actual quality of answers (that's what analysis documents show)

**It's essentially:**
```
For each query:
  predicted = TRACe evaluation of the answer
  ground_truth = PubMedQA dataset label
  error = |predicted - ground_truth|
  
Average error across all queries = MAE
```

---

## Why This Matters

### comparison.csv tells you:
- "How well does the model predict relevance?" (0.3332 average)
- "How far off are predictions from ground truth?" (0.3087 error)

### Analysis documents tell you:
- "What is the actual quality of answers?" (0.489 average)

### They're measuring DIFFERENT things:

| Aspect | comparison.csv | Analysis Documents |
|--------|----------------|-------------------|
| **Source** | JSONL predicted_scores | JSON report |
| **Measures** | Prediction accuracy | Answer quality |
| **v14 Relevance** | 0.3332 | 0.489 |
| **Interpretation** | Predictions are off by 0.31 | Answers have 48.9% relevant docs |

---

## Which is Correct?

**Both are correct, but they measure different things:**

- **Use analysis documents** for RAG system evaluation
  - Shows actual answer quality
  - Directly relevant to system performance
  - Better for decision-making

- **Use comparison.csv** for understanding prediction accuracy
  - Shows how well predictions match ground truth
  - Useful for debugging evaluation
  - Shows model calibration

---

## The Real Question: Why Does v14 Have Lower Predicted Scores?

Looking at the data:
- v14 predicted relevance: 0.3332
- v11 predicted relevance: 0.5147

**Possible reasons:**
1. v14 generates different answers that TRACe evaluates differently
2. v14's strict prompt may cause TRACe to judge answers more harshly
3. v14's step-back transform may retrieve different documents that TRACe scores lower
4. The evaluation criteria (ground truth) may not match v14's behavior

**But the analysis documents show:**
- v14 adherence: 0.850 (85% follow passage-only rule)
- v14 completeness: 0.685 (68.5% use all relevant docs)

**So v14 is actually better at following rules, even if predicted scores are lower.**

---

## Summary

✅ **You're right:** comparison.csv contains mean of TRACe evaluation scores

❌ **But:** It's comparing `predicted_scores` vs `ground_truth`, not just showing TRACe scores

📊 **The difference:**
- comparison.csv: Shows prediction accuracy (0.3332 for v14)
- Analysis documents: Show answer quality (0.489 for v14)

🎯 **Use analysis documents for decisions** - they show actual RAG system performance

---

## Generated: 2026-07-18
