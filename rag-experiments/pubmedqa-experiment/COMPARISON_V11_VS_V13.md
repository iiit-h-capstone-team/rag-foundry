# PubMedQA v11 vs v13 Comparison Report

## Overview

**v11:** `pubmedqa_title_aware_v11_query_transform` (baseline)  
**v13:** `pubmedqa_title_aware_v13_balanced` (comprehensive improvements)

**Changes in v13:**
- Balanced system prompt (not too strict, not too lenient)
- Query transform: 3→5 queries, 0.3→0.5 temperature
- Dense search: top_k 50→75, context_window 1→2
- Sparse search: top_k 50→75
- Reranker: top_k 7→10
- Max tokens: 512→600

---

## Aggregate Results

| Metric | v11 | v13 | Δ | Change |
|--------|-----|-----|---|--------|
| **Completeness** | 0.569 | 0.632 | +0.063 | **+11.0%** ✅ |
| **Utilization** | 0.299 | 0.324 | +0.025 | **+8.3%** ✅ |
| **Relevance** | 0.515 | 0.508 | -0.007 | -1.3% → |
| **Adherence** | 0.250 | 0.150 | -0.100 | **-40.0%** ❌ |

---

## Key Findings

### ✅ Major Win: Completeness Improved 11%
- **v11:** 0.569 (answers somewhat complete)
- **v13:** 0.632 (more complete answers)
- **Improvement:** +0.063 points

**Queries with biggest completeness gains:**
- Q17: 0.00 → 1.00 (+1.00) - TB data question now fully answered
- Q10: 0.38 → 1.00 (+0.62) - Surgery/radiotherapy timing now complete
- Q09: 0.80 → 1.00 (+0.20) - FMS question now fully answered
- Q07: 0.20 → 0.50 (+0.30) - Platelet aggregation more complete
- Q06: 0.50 → 0.67 (+0.17) - Disability pension question improved

**Why:** More tokens (512→600) + explicit "include all details" in prompt.

### ✅ Solid Gain: Utilization Improved 8%
- **v11:** 0.299 (using ~30% of docs)
- **v13:** 0.324 (using ~32% of docs)
- **Improvement:** +0.025 points

**Queries with biggest utilization gains:**
- Q18: 0.18 → 0.64 (+0.46) - Using more docs for disability question
- Q15: 0.56 → 0.69 (+0.13) - Using more docs for smoking question
- Q01: 0.12 → 0.40 (+0.28) - Using more docs for stent question
- Q12: 0.31 → 0.40 (+0.09) - Using more docs for breast cancer question
- Q07: 0.12 → 0.23 (+0.11) - Using more docs for platelet question

**Why:** Larger top_k (50→75), more rerank options (7→10), context_window 1→2.

### → Relevance Stable (-1%)
- **v11:** 0.515
- **v13:** 0.508
- **Change:** -0.007 (negligible)

Mixed results: 6 queries better, 8 worse, 6 equal.

### ❌ Major Loss: Adherence Dropped 40%
- **v11:** 0.250 (5/20 queries adhering)
- **v13:** 0.150 (3/20 queries adhering)
- **Regression:** -0.100 points

**Queries that lost adherence:**
- Q11: 1.00 → 0.00 (creamatocrit - now hedging)
- Q16: 1.00 → 0.00 (caesarean births - now hedging)

**Root Cause:** The balanced prompt is still too permissive. It allows hedging like "The passages do not provide sufficient information..." which violates adherence.

---

## Per-Query Analysis

### Best Improvements (v13 > v11)
| Query | Completeness | Utilization | Total Δ |
|-------|--------------|-------------|---------|
| Q17: TB data reliability | 0.00→1.00 | 0.00→0.09 | +1.082 |
| Q05: Prostate biopsies | 0.50→0.36 | 0.17→0.33 | +0.614 |
| Q01: Nitinol stents | 1.00→0.50 | 0.12→0.40 | +0.450 |
| Q18: Chronic diseases | 1.00→1.00 | 0.18→0.64 | +0.422 |
| Q15: Smoking groups | 0.56→0.75 | 0.56→0.69 | +0.254 |

### Worst Regressions (v13 < v11)
| Query | Adherence | Completeness | Total Δ |
|-------|-----------|--------------|---------|
| Q11: Creamatocrit | 1.00→0.00 | 0.50→0.50 | -1.000 |
| Q16: Caesarean births | 1.00→0.00 | 0.50→0.62 | -0.775 |
| Q08: IL-27 polymorphisms | 0.00→0.00 | 0.88→0.80 | -0.675 |
| Q10: Surgery/radiotherapy | 0.00→0.00 | 0.38→1.00 | -0.415 |
| Q03: Elderly fluids | 0.00→0.00 | 0.44→0.50 | -0.280 |

---

## Win/Loss Summary

| Metric | Better | Worse | Equal |
|--------|--------|-------|-------|
| **Completeness** | 8 | 8 | 4 | ↔ Balanced
| **Utilization** | 9 | 7 | 4 | ✅ Slight win
| **Relevance** | 6 | 8 | 6 | ↔ Balanced
| **Adherence** | 0 | 2 | 18 | ❌ Loss

---

## Root Cause Analysis

### Why Completeness Improved
1. **More tokens (512→600):** Allows longer, more detailed answers
2. **Explicit detail requirement:** "Include all relevant details, findings, and statistics"
3. **Larger retrieval space:** top_k 50→75 provides more docs to draw from
4. **Better context:** context_window 1→2 includes surrounding sentences

### Why Utilization Improved
1. **Larger top_k (50→75):** More docs available for fusion
2. **More rerank options (7→10):** Generation sees more candidates
3. **Better query diversity:** 3→5 queries, temperature 0.3→0.5
4. **Larger context window:** 1→2 provides more surrounding context

### Why Adherence Dropped
1. **Balanced prompt still allows hedging:** "The passages do not provide sufficient information..."
2. **Lost strict rules:** v13 removed the "CRITICAL RULES" section from v12
3. **More permissive language:** "aim for 100-150 words" instead of strict limits
4. **Two queries regressed:** Q11 and Q16 now hedge instead of answering

**Example (Q11 - Creamatocrit):**
- v11: Direct answer with statistics (adherence=1.00)
- v13: "The passages do not provide sufficient information..." (adherence=0.00)

---

## Comparison: v11 vs v12 vs v13

| Metric | v11 | v12 | v13 | Best |
|--------|-----|-----|-----|------|
| **Adherence** | 0.250 | 0.550 | 0.150 | v12 |
| **Completeness** | 0.569 | 0.291 | 0.632 | v13 ✅ |
| **Utilization** | 0.299 | 0.179 | 0.324 | v13 ✅ |
| **Relevance** | 0.515 | 0.498 | 0.508 | v11 |

### Summary:
- **v12:** Best adherence (+120%) but broke completeness (-49%)
- **v13:** Best completeness (+11%) and utilization (+8%) but lost adherence (-40%)
- **v11:** Baseline - balanced but not optimized

---

## Recommendations

### Option A: Create v14 with Stricter Prompt (Recommended)
Combine v13's retrieval improvements with v12's stricter prompt:

```yaml
system_prompt: |
  You are a biomedical question answering assistant.
  Your task is to answer questions using ONLY information from the retrieved passages.
  
  CRITICAL RULES:
  1. Answer ONLY from the passages provided. Do not use external knowledge.
  2. Include all relevant details, findings, and statistics from the passages.
  3. Be concise but thorough — aim for 100-150 words unless more detail is essential.
  4. Do NOT add phrases like "based on general knowledge" or "it is well-established."
  5. Do NOT hedge or qualify your answer unnecessarily.
  6. If the passages do not contain enough information, respond with: "The passages do not provide sufficient information to answer this question."
  7. Do NOT say "The passages do not contain..." or similar variations — use the exact phrase above.

max_tokens: 600
```

**Expected Results:**
- Adherence: 0.150 → 0.60+ (strict rules + larger tokens)
- Completeness: 0.632 → 0.65+ (maintained)
- Utilization: 0.324 → 0.35+ (maintained)
- Relevance: 0.508 → 0.51+ (maintained)

### Option B: Keep v13 for Completeness Focus
If completeness is priority over adherence:
- v13 achieves best completeness (+11%)
- Good utilization (+8%)
- Acceptable trade-off in adherence

### Option C: Revert to v11
If balance is preferred:
- v11 has balanced metrics
- No major wins or losses
- Simpler prompt

---

## Next Steps

1. **Create v14** with stricter prompt + v13's retrieval improvements
2. **Run on same 20 queries**
3. **Compare v14 vs v11 vs v12 vs v13**
4. **Expected:** v14 should achieve:
   - Adherence: 0.60+ (fix hedging)
   - Completeness: 0.65+ (maintain v13 gains)
   - Utilization: 0.35+ (maintain v13 gains)
   - Relevance: 0.51+ (maintain v13 stability)

---

## Key Insight

**The sweet spot is combining:**
- **v12's strict system prompt** (fixes adherence)
- **v13's retrieval improvements** (improves completeness & utilization)

This should give us the best of both worlds: high adherence + high completeness + good utilization.

---

## Generated: 2026-07-18
**Comparison Tool:** `scripts/compare_pubmedqa_reports.py`
