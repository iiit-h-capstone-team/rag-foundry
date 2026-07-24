# PubMedQA v11 vs v12 Comparison Report

## Overview

**v11:** `pubmedqa_title_aware_v11_query_transform` (baseline)  
**v12:** `pubmedqa_title_aware_v12_improved_prompt` (improved system prompt)

**Change:** Only the system prompt was modified to enforce stricter adherence rules.

---

## Aggregate Results

| Metric | v11 | v12 | Δ | Change |
|--------|-----|-----|---|--------|
| **Adherence** | 0.250 | 0.550 | +0.300 | **+120.0%** ✅ |
| **Completeness** | 0.569 | 0.291 | -0.279 | **-48.9%** ❌ |
| **Utilization** | 0.299 | 0.179 | -0.121 | **-40.3%** ❌ |
| **Relevance** | 0.515 | 0.498 | -0.017 | -3.3% ↓ |

---

## Key Findings

### ✅ Major Win: Adherence Improved 120%
- **v11:** 0.250 (only 5/20 queries adhering to passages)
- **v12:** 0.550 (11/20 queries adhering)
- **Improvement:** +6 queries now follow passage-only rule

**Queries Fixed:**
- Q01: 0.00 → 1.00 (prosthetic covering of nitinol stents)
- Q05: 0.00 → 1.00 (prostate biopsies mandatory)
- Q12: 0.00 → 1.00 (T1a breast cancers)
- Q18: 0.00 → 1.00 (association of chronic diseases)
- Q19: 0.00 → 1.00 (metabolic disorders)

### ❌ Major Loss: Completeness Dropped 49%
- **v11:** 0.569 (answers include details)
- **v12:** 0.291 (answers too brief)
- **Regression:** -9 queries lost completeness

**Root Cause:** Stricter prompt rules made model more conservative, cutting answers short.

**Affected Queries:**
- Q00: 0.71 → 0.47 (PEEK porosity - lost details)
- Q04: 0.71 → 0.00 (economic/social factors - no answer)
- Q08: 0.88 → 0.20 (IL-27 polymorphisms - minimal answer)
- Q09: 0.80 → 0.75 (Functional Movement Screen - brief)
- Q10: 0.38 → 0.00 (surgery/radiotherapy timing - no answer)

### ⚠️ Utilization Also Dropped 40%
- **v11:** 0.299 (using ~30% of retrieved docs)
- **v12:** 0.179 (using ~18% of retrieved docs)
- **Regression:** -11 queries use fewer documents

**Pattern:** Stricter adherence rules caused model to cite fewer docs, reducing utilization.

### → Relevance Stable (-3%)
- Minimal change in relevance scores
- Retrieval quality unchanged

---

## Per-Query Analysis

### Best Improvements (v12 > v11)
| Query | Adherence | Completeness | Total Δ |
|-------|-----------|--------------|---------|
| Q03: Do elderly persons need fluids? | 0.00→0.00 | 0.44→0.78 | +0.510 |
| Q12: Do T1a breast cancers profit? | 0.00→1.00 | 1.00→0.25 | +0.468 |
| Q05: Are prostate biopsies mandatory? | 0.00→1.00 | 0.50→0.00 | +0.417 |
| Q13: Blood donation mobile apps? | 1.00→1.00 | 0.45→0.64 | +0.307 |
| Q16: Going public - caesarean births? | 1.00→1.00 | 0.50→0.62 | +0.225 |

### Worst Regressions (v12 < v11)
| Query | Adherence | Completeness | Total Δ |
|-------|-----------|--------------|---------|
| Q10: Surgery/radiotherapy timing | 0.00→0.00 | 0.38→0.00 | -1.297 |
| Q04: Economic/social factors | 0.00→0.00 | 0.71→0.00 | -1.214 |
| Q08: IL-27 polymorphisms | 0.00→1.00 | 0.88→0.20 | -0.508 |
| Q02: Diabetes prognostic factor | 0.00→0.00 | 0.33→0.00 | -0.410 |
| Q00: PEEK porosity | 1.00→1.00 | 0.71→0.47 | -0.365 |

---

## Win/Loss Summary

| Metric | Better | Worse | Equal |
|--------|--------|-------|-------|
| **Adherence** | 6 | 0 | 14 | ✅ Pure win
| **Completeness** | 4 | 13 | 3 | ❌ Major loss
| **Utilization** | 3 | 14 | 3 | ❌ Major loss
| **Relevance** | 8 | 7 | 5 | → Neutral

---

## Root Cause Analysis

### Why Completeness Dropped

The improved system prompt added stricter rules:
```
1. Answer ONLY from the passages provided. Do not use any external knowledge.
2. If the passages contain the answer, provide it directly and completely.
3. If the passages do NOT contain enough information to answer, respond with: "The passages do not contain sufficient information to answer this question."
```

**Problem:** Rule #3 made the model too conservative. When uncertain, it now says "passages do not contain" instead of attempting an answer with available information.

**Example (Q10):**
- v11: "The study aimed to evaluate the influence of prognostic factors in postoperative radiotherapy of NSCLC with special emphasis on the time interval between surgery and start of radiotherapy." (0.38 completeness)
- v12: "The passages do not contain sufficient information to answer this question." (0.00 completeness)

### Why Adherence Improved

The explicit rules forced the model to:
1. Not hedge with "based on general knowledge"
2. Use exact phrase "The passages do not contain..." instead of variations
3. Avoid adding external knowledge

This worked for 6 queries where the model was previously hedging.

---

## Recommendations

### Option A: Find Middle Ground
Modify system prompt to be less strict:
```yaml
system_prompt: |
  You are a biomedical question answering assistant.
  Answer ONLY from the retrieved passages.
  Include all relevant details from the passages.
  If passages lack information, say: "The passages do not provide sufficient information."
  Do NOT add external knowledge or hedge.
```

**Expected:** Adherence 0.55 → 0.70, Completeness 0.29 → 0.50

### Option B: Revert to v11 + Selective Fixes
Keep v11 but fix specific adherence issues (Q2, Q3, Q4, Q5, Q6, Q17, Q18, Q19).

**Expected:** Adherence 0.25 → 0.60, Completeness stays 0.57

### Option C: Create v13 with Balanced Prompt
```yaml
system_prompt: |
  You are a biomedical question answering assistant.
  Answer ONLY from the retrieved passages below.
  Be concise but complete — include all relevant details and findings.
  Do NOT add information from your own knowledge.
  Do NOT hedge with phrases like "based on general knowledge."
  If the passages do not contain enough information, say: "The passages do not provide sufficient information to answer this question."
```

**Expected:** Adherence 0.55, Completeness 0.50, Utilization 0.30

---

## Conclusion

**v12 achieved the goal of improving adherence (+120%)** but at the cost of completeness (-49%) and utilization (-40%).

The stricter prompt rules were too aggressive. A balanced approach (Option C) would likely achieve:
- Adherence: 0.55+ (fixed hedging)
- Completeness: 0.50+ (still detailed)
- Utilization: 0.30+ (uses more docs)

**Recommendation:** Create v13 with a balanced prompt that enforces adherence without sacrificing completeness.

---

## Generated: 2026-07-18
**Comparison Tool:** `scripts/compare_pubmedqa_reports.py`
