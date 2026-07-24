# V16 Testing and Comparison Guide

## Overview

This guide explains how to run v16 and compare it against v14.

---

## Step 1: Verify Configuration

Check that v16 config exists:

```bash
ls -la rag-experiments/pubmedqa-experiment/config/pubmedqa_v16_improved_retrieval.yaml
```

Expected output:
```
-rw-r--r--  1 user  group  3.2K Jul 19 12:00 pubmedqa_v16_improved_retrieval.yaml
```

---

## Step 2: Run V16 Experiment

### Option A: Using Experiment Runner (Recommended)

The experiment runner will automatically run v16 on all 20 queries:

```bash
cd /Users/aditya.narayan/git-personal/rag-foundry
python3 -m experiment.experiment_runner rag-experiments/pubmedqa-experiment/experiment_config.yaml
```

This will:
1. Load v16 configuration
2. Run on all 20 queries
3. Evaluate using TRACe
4. Save results to `temp/pubmedqa_title_aware_v16_improved_retrieval.jsonl`
5. Generate report to `reports/pubmedqa_title_aware_v16_improved_retrieval.json`

**Expected time:** 10-15 minutes

### Option B: Using Script

```bash
cd /Users/aditya.narayan/git-personal/rag-foundry
python3 scripts/run_v16_experiment.py
```

---

## Step 3: Compare V14 vs V16

After v16 completes, run the comparison script:

```bash
cd /Users/aditya.narayan/git-personal/rag-foundry
python3 scripts/compare_v14_vs_v16.py
```

This will:
1. Load v14 results from `temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl`
2. Load v16 results from `temp/pubmedqa_title_aware_v16_improved_retrieval.jsonl`
3. Compare predicted scores
4. Compare against ground truth
5. Show per-query improvements
6. Generate summary

**Output:** Detailed comparison table with metrics

---

## Expected Results

### Predicted Score Improvements

| Metric | v14 | v16 Expected | Improvement |
|--------|-----|--------------|-------------|
| **Relevance** | 0.3332 | 0.42-0.48 | +26-44% |
| **Utilization** | 0.0822 | 0.25-0.35 | +204-326% |
| **Completeness** | 0.1717 | 0.45-0.55 | +162-220% |

### Ground Truth Alignment

| Metric | Ground Truth | v14 Gap | v16 Gap | Improvement |
|--------|--------------|---------|---------|-------------|
| **Relevance** | 0.4885 | -0.1553 | -0.01 to -0.07 | +0.09-0.15 |
| **Utilization** | 0.3699 | -0.2878 | -0.02 to -0.12 | +0.17-0.27 |
| **Completeness** | 0.6849 | -0.5133 | -0.23 to -0.33 | +0.18-0.28 |

---

## Interpretation

### Success Indicators

✅ **Excellent:** All metrics improve by >10%
- Relevance: > 0.45
- Utilization: > 0.30
- Completeness: > 0.50

✓ **Good:** Most metrics improve by >5%
- Relevance: > 0.40
- Utilization: > 0.20
- Completeness: > 0.40

⚠️ **Partial:** Some metrics improve, some don't
- Mixed results across metrics

❌ **Failed:** No improvement or regression
- Metrics stay same or decrease

---

## Troubleshooting

### Issue: v16 config not found

**Solution:**
```bash
# Verify config exists
ls rag-experiments/pubmedqa-experiment/config/pubmedqa_v16_improved_retrieval.yaml

# If not, recreate it
# See V16_IMPROVED_RETRIEVAL_GUIDE.md
```

### Issue: v16 experiment fails

**Solution:**
```bash
# Check logs
tail -100 rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v16_improved_retrieval.jsonl

# Check for API errors
# Verify GROQ_API_KEY is set
echo $GROQ_API_KEY

# Try running single query
python3 -m rag.pipeline.rag_pipeline --config config/pubmedqa_v16_improved_retrieval.yaml --query "test query"
```

### Issue: Comparison script fails

**Solution:**
```bash
# Verify v16 results exist
ls rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v16_improved_retrieval.jsonl

# If not, run v16 first
python3 scripts/run_v16_experiment.py

# Then run comparison
python3 scripts/compare_v14_vs_v16.py
```

---

## Next Steps After Comparison

### If V16 Shows Improvement (>10% on all metrics)

1. **Declare v16 as new baseline**
   - Use v16 for production
   - Archive v14 results

2. **Plan v17 for further improvement**
   - Try alternative embedding (SciBERT)
   - Try alternative reranker (DeBERTa)
   - Try hybrid query transform

3. **Document findings**
   - Create COMPARISON_V14_VS_V16.md
   - Update ANALYSIS_SUMMARY.md

### If V16 Shows Partial Improvement (5-10% on some metrics)

1. **Analyze which metrics improved**
   - Relevance improved? → Query transform working
   - Utilization improved? → Longer answers helping
   - Completeness improved? → More documents helping

2. **Plan v17 to address remaining issues**
   - If relevance still low → Try different embedding
   - If utilization still low → Try different prompt
   - If completeness still low → Try different reranker

3. **Consider hybrid approach**
   - Combine v16 with alternative strategies
   - Test multiple configurations in parallel

### If V16 Shows No Improvement or Regression

1. **Investigate root cause**
   - Check if multi_query is working
   - Verify reranker is using more documents
   - Check if longer answers are being generated

2. **Revert to v14 or try alternative**
   - Use v14 as baseline
   - Try v17 with different approach (SciBERT, DeBERTa)
   - Consider ensemble approach

3. **Document findings**
   - Create COMPARISON_V14_VS_V16.md with findings
   - Explain why v16 didn't work
   - Propose alternative strategies

---

## Files

- **Config:** `config/pubmedqa_v16_improved_retrieval.yaml`
- **Guide:** `V16_IMPROVED_RETRIEVAL_GUIDE.md`
- **Testing:** `V16_TESTING_GUIDE.md` (this file)
- **Comparison Script:** `scripts/compare_v14_vs_v16.py`
- **Run Script:** `scripts/run_v16_experiment.py`

---

## Timeline

| Step | Time | Status |
|------|------|--------|
| 1. Verify config | 1 min | ✓ |
| 2. Run v16 | 10-15 min | ⏳ |
| 3. Compare | 1 min | ⏳ |
| 4. Analyze | 5-10 min | ⏳ |
| 5. Plan next | 5 min | ⏳ |

**Total:** ~30-40 minutes

---

## Generated: 2026-07-19
