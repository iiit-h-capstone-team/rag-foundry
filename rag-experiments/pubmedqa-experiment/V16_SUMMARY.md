# V16 Configuration Summary

## Quick Overview

**v16** addresses v14's critical underperformance by improving retrieval and generation.

---

## Key Changes (7 modifications)

| Component | v14 | v16 | Why |
|-----------|-----|-----|-----|
| **Query Transform** | step_back | multi_query (5 queries) | Better query coverage |
| **Dense Search top_k** | 75 | 100 | More candidates |
| **Sparse Search top_k** | 75 | 100 | More candidates |
| **Min Similarity** | 0.5 | 0.4 | Less strict filtering |
| **Reranker top_k** | 15 | 25 | More documents in context |
| **Max Tokens** | 600 | 800 | Longer answers |
| **System Prompt** | Concise (100-150w) | Thorough (200-300w) | Encourage usage |

---

## Expected Improvements

| Metric | v14 | v16 Expected | Improvement |
|--------|-----|--------------|-------------|
| **Relevance** | 0.3332 | 0.42-0.48 | **+26-44%** |
| **Utilization** | 0.0822 | 0.25-0.35 | **+204-326%** |
| **Completeness** | 0.1717 | 0.45-0.55 | **+162-220%** |
| **Adherence** | 0.850 | 0.80-0.85 | -0-5% |

---

## Ground Truth Alignment

| Metric | Ground Truth | v16 Expected | Gap |
|--------|--------------|--------------|-----|
| **Relevance** | 0.4885 | 0.42-0.48 | -2-14% |
| **Utilization** | 0.3699 | 0.25-0.35 | -5-32% |
| **Completeness** | 0.6849 | 0.45-0.55 | -20-34% |

**Status:** Still underperforming, but significantly improved from v14

---

## Files

- **Config:** `config/pubmedqa_v16_improved_retrieval.yaml`
- **Guide:** `V16_IMPROVED_RETRIEVAL_GUIDE.md`
- **Design:** `scripts/design_v16_config.py`

---

## Next Steps

1. Run v16 on 5 problem queries (Q01, Q03, Q04, Q09, Q15)
2. Compare against v14 and ground truth
3. If promising, run on all 20 queries
4. Generate comparison report
5. Plan v17 if needed

---

## Success Criteria

- ✅ Relevance > 0.40 (vs v14's 0.3332)
- ✅ Utilization > 0.20 (vs v14's 0.0822)
- ✅ Completeness > 0.40 (vs v14's 0.1717)
- ✅ Adherence > 0.80 (vs v14's 0.850)

---

Generated: 2026-07-19
