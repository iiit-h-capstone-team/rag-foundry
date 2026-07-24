# V16 Revised: Adherence-Focused Configuration

## Critical Issue Identified

**Adherence Score Drop in Original V16:**
- v14 adherence: 0.850 (17/20 queries follow passage-only rule)
- v16 original adherence: Expected 0.80-0.85 (risk of drop)
- **Problem:** Longer answers and more documents can lead to hallucination

---

## V16 Revised: Adherence Safeguards

### Key Changes to Maintain Adherence

| Component | v14 | v16 Original | v16 Revised | Rationale |
|-----------|-----|--------------|-------------|-----------|
| **Query Transform Temp** | 0.3 | 0.5 | 0.3 | Lower temp = more consistent queries |
| **Dense Search top_k** | 75 | 100 | 85 | Balance: more candidates but not too many |
| **Sparse Search top_k** | 75 | 100 | 85 | Balance: more candidates but not too many |
| **Min Similarity** | 0.5 | 0.4 | 0.5 | Keep strict filtering |
| **Reranker top_k** | 15 | 25 | 20 | More docs but not overwhelming |
| **Max Tokens** | 600 | 800 | 700 | Longer but not too long |
| **System Prompt** | Strict | Thorough | Strict + Thorough | Enforce adherence explicitly |

---

## System Prompt Enhancements

### V14 Prompt (Baseline)
```
Be concise but complete — include all relevant details from the passages.
Aim for 100-150 words unless more detail is essential.
```

### V16 Revised Prompt (Adherence-Focused)
```
CRITICAL RULES (MUST FOLLOW ALL):
1. Answer ONLY from the passages provided. Do not use external knowledge.
2. Include ALL relevant details, findings, statistics, and information.
3. Be thorough and comprehensive — aim for 150-250 words.
4. Do NOT add phrases like "based on general knowledge", "it is well-established".
5. Do NOT hedge with "may", "might", "could", "possibly" unless in passages.
6. Every claim must be directly traceable to the passages.
7. Do NOT add interpretations, conclusions, or inferences not explicitly stated.
```

**Key Additions:**
- Explicit list of forbidden hedging phrases
- Requirement for traceability
- Prohibition on interpretations/inferences
- Stricter word count guidance (150-250 vs 200-300)

---

## Expected Results: V16 Revised

### Predicted Improvements

| Metric | v14 | v16 Revised | Improvement | Status |
|--------|-----|-------------|-------------|--------|
| **Relevance** | 0.3332 | 0.40-0.45 | +20-35% | ✅ |
| **Utilization** | 0.0822 | 0.20-0.28 | +143-240% | ✅ |
| **Completeness** | 0.1717 | 0.35-0.45 | +104-162% | ✅ |
| **Adherence** | 0.850 | 0.85-0.90 | MAINTAINED | ✅ |

### Ground Truth Alignment

| Metric | Ground Truth | v14 Gap | v16 Gap | Improvement |
|--------|--------------|---------|---------|-------------|
| **Relevance** | 0.4885 | -0.1553 | -0.04 to -0.09 | +0.06-0.12 |
| **Utilization** | 0.3699 | -0.2878 | -0.09 to -0.17 | +0.12-0.20 |
| **Completeness** | 0.6849 | -0.5133 | -0.23 to -0.33 | +0.18-0.28 |
| **Adherence** | 0.850 | 0.000 | 0.000 to +0.05 | MAINTAINED |

---

## Configuration Details

### Query Transform
```yaml
query_transform:
  type: multi_query
  config:
    num_queries: 5
    temperature: 0.3  # Lower for consistency
```

**Why multi_query?**
- Generates 5 alternative query phrasings
- Temperature 0.3 keeps them on-topic
- Better coverage than step_back alone
- Helps with diverse query types

### Search Configuration
```yaml
search:
  searches:
    - type: dense
      config:
        top_k: 85  # Balanced
        min_similarity: 0.5  # Strict filtering
    - type: sparse
      config:
        top_k: 85  # Balanced
```

**Why these values?**
- 85 is between v14 (75) and original v16 (100)
- More candidates than v14, but not overwhelming
- min_similarity 0.5 filters out borderline docs
- Reduces noise that could cause hallucination

### Reranking
```yaml
rerank:
  type: cross_encoder
  config:
    model_name: BAAI/bge-reranker-v2-m3
    top_k: 20  # Balanced
```

**Why top_k 20?**
- More than v14 (15) for better coverage
- Less than original v16 (25) to avoid confusion
- 20 documents fit in context window
- Reranker picks best from larger pool

### Generation
```yaml
generation:
  config:
    max_tokens: 700  # Balanced
    temperature: 0.0  # Deterministic
```

**Why 700 tokens?**
- More than v14 (600) for comprehensive answers
- Less than original v16 (800) to prevent rambling
- ~175-225 words at typical token rate
- Enough for detailed answers without hallucination

---

## Adherence Safeguards

### 1. Strict System Prompt
- Explicit list of forbidden phrases
- Requirement for traceability
- Prohibition on interpretations
- Clear word count guidance

### 2. Lower Query Transform Temperature
- 0.3 instead of 0.5
- Keeps generated queries on-topic
- Reduces irrelevant document retrieval
- More consistent behavior

### 3. Strict Document Filtering
- min_similarity 0.5 (not 0.4)
- Only high-confidence documents
- Reduces noise and confusion
- Fewer irrelevant passages

### 4. Balanced Retrieval
- top_k 85 (not 100)
- More candidates than v14
- Not overwhelming the model
- Better signal-to-noise ratio

### 5. Deterministic Generation
- temperature 0.0
- No randomness
- Consistent adherence
- Reproducible results

---

## Risk Assessment

### Potential Issues & Mitigations

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Adherence still drops | Low | Strict prompt + lower temp |
| Relevance doesn't improve | Medium | More documents (85 vs 75) |
| Utilization still low | Low | Longer answers (700 tokens) |
| Latency increases | Low | Balanced top_k values |

### Fallback Plan

If v16 revised still has issues:

**If adherence drops below 0.80:**
- Reduce max_tokens to 650
- Reduce reranker top_k to 15
- Use step_back instead of multi_query

**If relevance doesn't improve:**
- Increase dense search top_k to 100
- Reduce min_similarity to 0.45
- Try different embedding model (v17)

**If utilization still low:**
- Increase max_tokens to 750
- Increase reranker top_k to 25
- Relax system prompt slightly

---

## Testing Strategy

### Phase 1: Quick Validation (5 queries)
```
Test on problem queries: Q01, Q03, Q04, Q09, Q15
Check: Adherence maintained, other metrics improved
```

### Phase 2: Full Test (20 queries)
```
Run all queries
Compare against v14 and ground truth
Verify adherence >= 0.80
```

### Phase 3: Analysis
```
Per-query breakdown
Identify any regressions
Verify improvements
```

---

## Success Criteria

### Minimum Success
- ✅ Adherence >= 0.80 (vs v14's 0.850)
- ✅ Relevance > 0.40 (vs v14's 0.3332)
- ✅ Utilization > 0.20 (vs v14's 0.0822)
- ✅ Completeness > 0.35 (vs v14's 0.1717)

### Target Success
- ✅ Adherence >= 0.85 (maintain v14 level)
- ✅ Relevance > 0.43 (vs ground truth's 0.4885)
- ✅ Utilization > 0.25 (vs ground truth's 0.3699)
- ✅ Completeness > 0.40 (vs ground truth's 0.6849)

### Excellent Success
- ✅ Adherence >= 0.85 (maintain v14 level)
- ✅ Relevance > 0.45 (close to ground truth)
- ✅ Utilization > 0.30 (close to ground truth)
- ✅ Completeness > 0.50 (close to ground truth)

---

## Summary

**V16 Revised balances improvement with safety:**

| Aspect | Approach |
|--------|----------|
| **Adherence** | Strict prompt + lower temp + balanced retrieval |
| **Relevance** | More documents (85) + multi_query (5) |
| **Utilization** | Longer answers (700) + more docs (20 reranker) |
| **Completeness** | More docs + longer answers + strict filtering |

**Key Philosophy:**
- Conservative improvements
- Maintain adherence (critical for RAG)
- Incremental gains on other metrics
- Safe fallback options

---

## Files

- **Config:** `config/pubmedqa_v16_improved_retrieval.yaml` (UPDATED)
- **Guide:** `V16_IMPROVED_RETRIEVAL_GUIDE.md`
- **This Document:** `V16_REVISED_ADHERENCE_FOCUS.md`
- **Analysis:** `scripts/analyze_adherence_issue.py`

---

## Generated: 2026-07-19
