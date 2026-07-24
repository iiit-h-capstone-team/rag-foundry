# PubMedQA v14 - Domain-Specific Embedding & Query Transform

## Overview

v14 combines the best improvements from previous versions with domain-specific enhancements:

1. **PubMedBERT Embedding** - Biomedical-specific instead of general-purpose
2. **Step-Back Query Transform** - Better for complex, multi-faceted queries
3. **Weighted Fusion** - Optimized dense/sparse balance for biomedical domain
4. **Strict System Prompt** - From v12, prevents hedging
5. **Enhanced Retrieval** - Larger top_k, better reranker

---

## Key Changes from v13

### 1. Embedding Model Upgrade 🧠

**From:** BAAI/bge-large-en-v1.5 (general-purpose, 1024 dims)
**To:** microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext (biomedical, 768 dims)

```yaml
# v13
embedding:
  type: sentence_transformer
  config:
    model_name: BAAI/bge-large-en-v1.5
    dimension: 1024

# v14
embedding:
  type: sentence_transformer
  config:
    model_name: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
    dimension: 768
```

**Why PubMedBERT:**
- Trained on 18M PubMed abstracts + full-text articles
- Understands biomedical terminology and concepts
- Better at capturing domain-specific relationships
- Proven on biomedical Q&A benchmarks
- Dimension reduction (1024→768) is acceptable for domain-specific model

**Expected Impact:**
- Relevance: 0.508 → 0.60+ (+18%)
- Utilization: 0.324 → 0.38+ (+17%)
- Better handling of medical terminology

---

### 2. Query Transform Strategy 🔄

**From:** Multi-Query (generates 5 variations)
**To:** Step-Back (breaks complex queries into simpler sub-questions)

```yaml
# v13
retrieval:
  query_transform:
    type: multi_query
    config:
      num_queries: 5
      temperature: 0.5

# v14
retrieval:
  query_transform:
    type: step_back
    config:
      model: llama-3.3-70b-versatile
      temperature: 0.3
```

**Why Step-Back:**
- Better for complex, multi-faceted queries (Q06, Q10, Q17)
- Breaks down: "Do working conditions explain disability pension?" → "What are working conditions?", "What causes disability pension?", "Is there a link?"
- Captures nuance better than simple variations
- Helps with geographic/specific details (Q17 - Benin TB data)
- More effective for recommendation questions (Q03 - elderly fluids)

**How Step-Back Works:**
1. Takes original query
2. Generates simpler, more fundamental sub-questions
3. Retrieves for each sub-question
4. Combines results for comprehensive coverage

**Expected Impact:**
- Relevance: 0.508 → 0.55+ (better query intent capture)
- Utilization: 0.324 → 0.35+ (more relevant docs retrieved)
- Fixes problem queries: Q06, Q10, Q17, Q03

---

### 3. Fusion Strategy Optimization ⚖️

**From:** RRF (Reciprocal Rank Fusion)
**To:** Weighted Sum (0.7 dense, 0.3 sparse)

```yaml
# v13
retrieval:
  fusion:
    type: rrf
    config:
      k: 60

# v14
retrieval:
  fusion:
    type: weighted_sum
    config:
      dense_weight: 0.7
      sparse_weight: 0.3
```

**Why Weighted Sum:**
- Dense (semantic) captures meaning: 70% weight
- Sparse (keyword) catches specific terms: 30% weight
- Better for biomedical domain where terminology matters
- RRF treats both equally, but semantic is more important for Q&A

**Example:**
- Query: "Do prostate biopsies mandatory..."
- Dense: Captures semantic meaning of "mandatory"
- Sparse: Catches exact term "prostate biopsy"
- Weighted: Balances both for better results

**Expected Impact:**
- Relevance: +2-3% (better balance)
- Utilization: +2-3% (more relevant docs)

---

### 4. Reranker Improvements 🎯

**From:** top_k=10
**To:** top_k=15

```yaml
# v13
retrieval:
  rerank:
    config:
      top_k: 10

# v14
retrieval:
  rerank:
    config:
      top_k: 15
```

**Why Increase to 15:**
- More options for generation to choose from
- Better coverage of edge cases
- Still manageable context size
- Minimal performance cost

**Expected Impact:**
- Utilization: +1-2% (more docs available)
- Relevance: +1% (better selection)

---

### 5. System Prompt - Strict Adherence 📝

**From:** Balanced (v13)
**To:** Strict (v12 style)

```yaml
# v13 (balanced)
system_prompt: |
  Your task is to answer questions using information from the retrieved passages.
  INSTRUCTIONS:
  1. Answer ONLY from the passages provided...
  6. If the passages do not contain enough information, say: "The passages do not provide sufficient information..."

# v14 (strict)
system_prompt: |
  Your task is to answer questions using ONLY information from the retrieved passages.
  CRITICAL RULES:
  1. Answer ONLY from the passages provided...
  6. If the passages do not contain enough information, respond with: "The passages do not provide sufficient information to answer this question."
  7. Do NOT say "The passages do not contain..." or similar variations — use the exact phrase above.
```

**Why Strict:**
- Prevents hedging variations
- Enforces exact phrase for insufficient info
- Fixes adherence issues from v13
- Combines with better retrieval (PubMedBERT) to avoid false "insufficient info"

**Expected Impact:**
- Adherence: 0.150 → 0.60+ (+300%)
- Completeness: 0.632 → 0.65+ (maintained with better retrieval)

---

## Configuration Summary

### Retrieval Changes
| Parameter | v13 | v14 | Change | Impact |
|-----------|-----|-----|--------|--------|
| Embedding | BGE-large | PubMedBERT | Domain-specific | Relevance +18% |
| Query Transform | multi_query | step_back | Better nuance | Relevance +5% |
| Fusion | RRF | weighted_sum | Better balance | Relevance +2% |
| Reranker top_k | 10 | 15 | More options | Util +2% |

### Generation Changes
| Parameter | v13 | v14 | Change |
|-----------|-----|-----|--------|
| System Prompt | Balanced | Strict | Prevents hedging |
| Max Tokens | 600 | 600 | Maintained |
| Temperature | 0.0 | 0.0 | Maintained |

---

## Expected Results

### Aggregate Metrics
| Metric | v11 | v13 | v14 Expected |
|--------|-----|-----|--------------|
| **Adherence** | 0.250 | 0.150 | 0.60+ ✅ |
| **Completeness** | 0.569 | 0.632 | 0.65+ ✅ |
| **Utilization** | 0.299 | 0.324 | 0.38+ ✅ |
| **Relevance** | 0.515 | 0.508 | 0.60+ ✅ |

### Problem Query Fixes
| Query | v13 Rel | v14 Expected | Fix |
|-------|---------|--------------|-----|
| Q10 (Surgery/RT) | 0.091 | 0.50+ | Step-back breaks into sub-questions |
| Q17 (TB Data) | 0.091 | 0.40+ | PubMedBERT understands context |
| Q06 (Disability) | 0.136 | 0.45+ | Step-back captures multi-faceted nature |
| Q03 (Elderly) | 0.286 | 0.50+ | Better query understanding |

---

## Why This Combination Works

### PubMedBERT + Step-Back Synergy

1. **PubMedBERT** provides domain-aware embeddings
   - Understands biomedical concepts
   - Better semantic space for medical Q&A
   - Fixes relevance scoring issues

2. **Step-Back** provides better query understanding
   - Breaks complex queries into components
   - Captures multi-faceted aspects
   - Handles nuanced questions better

3. **Together** they address the root cause:
   - v13 had good retrieval accuracy (100%) but poor relevance scoring
   - PubMedBERT fixes relevance scoring
   - Step-Back fixes query understanding
   - Result: Better relevance + better utilization

---

## Testing Plan

### Step 1: Run v14 on 20 Queries
```bash
# Run experiment with v14 config
# This will generate: pubmedqa_title_aware_v14_pubmedbert_stepback.json
```

### Step 2: Compare Against Baselines
```bash
python3 scripts/compare_pubmedqa_reports.py \
  reports/pubmedqa_title_aware_v11_query_transform.json \
  reports/pubmedqa_title_aware_v14_pubmedbert_stepback.json
```

### Step 3: Analyze Results
- Check if relevance improved to 0.60+
- Check if adherence improved to 0.60+
- Check if problem queries (Q10, Q17, Q06, Q03) improved
- Compare against v12 and v13

### Step 4: Decision
- **If v14 > v13 & v12:** Use v14 as new baseline
- **If v14 < v13:** Revert to v13, try different embedding
- **If mixed:** Identify which changes helped, iterate

---

## Rollback Plan

If v14 underperforms:

1. **Keep PubMedBERT, revert to multi_query:**
   - PubMedBERT is good, step-back might not work for all queries
   - Try: `type: multi_query, num_queries: 7, temperature: 0.5`

2. **Keep step-back, revert to BGE:**
   - Step-back is good, embedding might need tuning
   - Try: `model_name: BAAI/bge-large-en-v1.5`

3. **Keep strict prompt, revert retrieval:**
   - Strict prompt is good, retrieval changes might not help
   - Try: v13 retrieval + v14 prompt

---

## Implementation Notes

### PubMedBERT Download
- Model size: ~500MB
- First run will download and cache
- Subsequent runs use cached version
- No additional dependencies needed

### Step-Back Query Transform
- Uses LLM to generate sub-questions
- Slightly more API calls than multi_query
- Temperature 0.3 keeps it focused (not too creative)
- Better for complex biomedical questions

### Weighted Fusion
- 0.7 dense + 0.3 sparse is standard for semantic search
- Can adjust if results don't improve
- Try 0.75/0.25 or 0.65/0.35 if needed

---

## Comparison: All Versions

| Metric | v11 | v12 | v13 | v14 Expected |
|--------|-----|-----|-----|--------------|
| Adherence | 0.250 | 0.550 | 0.150 | 0.60+ |
| Completeness | 0.569 | 0.291 | 0.632 | 0.65+ |
| Utilization | 0.299 | 0.179 | 0.324 | 0.38+ |
| Relevance | 0.515 | 0.498 | 0.508 | 0.60+ |

### Summary:
- **v11:** Baseline, balanced
- **v12:** Best adherence, broke completeness
- **v13:** Best completeness, lost adherence
- **v14:** Best of all - high adherence + high completeness + high relevance

---

## Generated: 2026-07-18
**Config:** `pubmedqa_v14_pubmedbert_stepback.yaml`
