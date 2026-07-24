# How Relevance Score is Calculated

## Quick Answer

**Relevance is calculated using ALL retrieved documents, not just the top 1.**

```python
# From evaluation/strategies/trace/strategy.py:177
relevance_score = len(relevant_keys) / total_doc_sentences
```

---

## Detailed Explanation

### What is "Relevance"?

**Relevance Score = (Number of relevant document sentences) / (Total document sentences)**

In other words:
- **Numerator:** How many sentences in ALL retrieved documents are relevant to the query?
- **Denominator:** How many total sentences are in ALL retrieved documents?

### Example

**Query:** "Do elderly persons need to be encouraged to drink more fluids?"

**Retrieved Documents (5 docs):**
1. Doc 1: 3 sentences (all about elderly dehydration)
2. Doc 2: 2 sentences (about fluid intake guidelines)
3. Doc 3: 4 sentences (about ICU care, not relevant)
4. Doc 4: 3 sentences (about nutritional screening, not relevant)
5. Doc 5: 2 sentences (about smoking and energy drinks, not relevant)

**Total sentences:** 3 + 2 + 4 + 3 + 2 = 14 sentences

**LLM judges which are relevant to the query:**
- Doc 1: 3 relevant (all about elderly dehydration)
- Doc 2: 2 relevant (about fluid intake)
- Doc 3: 0 relevant
- Doc 4: 0 relevant
- Doc 5: 0 relevant

**Total relevant sentences:** 3 + 2 = 5 sentences

**Relevance Score:** 5 / 14 = 0.357 (35.7%)

---

## The Four Metrics Explained

### 1. Relevance Score (0.489 in v14)
```
= (Relevant document sentences) / (Total document sentences)
= How many of the retrieved docs are actually relevant?
```

**Key insight:** This measures the QUALITY of the retrieved document set. If you retrieve 5 docs but only 2 are relevant, relevance is low.

### 2. Utilization Score (0.370 in v14)
```
= (Utilized document sentences) / (Total document sentences)
= How many of the retrieved docs did the model actually use?
```

**Key insight:** This measures whether the model USED the relevant documents. If 5 docs are relevant but the model only used 2, utilization is low.

### 3. Completeness Score (0.685 in v14)
```
= (Relevant AND utilized sentences) / (Relevant sentences)
= Of the relevant docs, how many did the model use?
```

**Key insight:** This measures whether the model used ALL relevant documents. If 5 docs are relevant and the model used 4, completeness is high (4/5 = 80%).

### 4. Adherence Score (0.850 in v14)
```
= Whether ALL response sentences are supported by documents
= True/False (boolean)
```

**Key insight:** This measures whether the model followed the "passage-only" rule.

---

## Why v14 Has Low Relevance (0.489)

### Root Cause: Poor Retrieval Quality

When you retrieve 5 documents per query, but only 2-3 are actually relevant to the query, the relevance score is low.

**Example from v14:**

**Q17 (TB data): rel=0.167**
- Retrieved 5 documents
- Total sentences: ~25
- Relevant sentences: ~4
- Relevance: 4/25 = 0.16

**Why?** The query asks about "Benin's National TB Programme" but the retrieved documents discuss TB in general, not specifically Benin's program.

**Q19 (Metabolic): rel=0.111**
- Retrieved 5 documents
- Total sentences: ~25
- Relevant sentences: ~3
- Relevance: 3/25 = 0.11

**Why?** The query asks about a very specific combination (metabolic disorders + BPH in aging men) but the retrieved documents discuss these topics separately.

---

## How to Improve Relevance

### Strategy 1: Better Retrieval (Semantic Similarity Threshold)
**Problem:** Retrieved documents are not relevant
**Solution:** Filter out low-similarity documents

```yaml
retrieval:
  search:
    searches:
      - type: dense
        config:
          min_similarity: 0.5  # Only keep docs with >0.5 similarity
```

**Effect:** Fewer documents retrieved, but higher quality
- Before: 5 docs, 4 relevant → rel = 4/25 = 0.16
- After: 3 docs, 3 relevant → rel = 3/15 = 0.20

### Strategy 2: Better Query Understanding (Query Rewriting)
**Problem:** Query is too complex, retrieval misses nuances
**Solution:** Rewrite query to be clearer

```
Original: "Can metabolic disorders in aging men contribute to prostatic hyperplasia?"
Rewritten: "Does metabolic syndrome cause benign prostatic hyperplasia in elderly males?"
```

**Effect:** Better matching between query and documents
- Before: 5 docs, 3 relevant → rel = 3/25 = 0.12
- After: 5 docs, 4 relevant → rel = 4/25 = 0.16

### Strategy 3: Better Embedding (Domain-Specific)
**Problem:** General-purpose embedding misses biomedical nuances
**Solution:** Use PubMedBERT (already done in v14)

**Effect:** Better semantic matching
- Before (BGE): 5 docs, 3 relevant → rel = 3/25 = 0.12
- After (PubMedBERT): 5 docs, 4 relevant → rel = 4/25 = 0.16

### Strategy 4: Better Ranking (Multi-Stage Retrieval)
**Problem:** Relevant documents are ranked low
**Solution:** Use multiple embeddings + cross-encoder reranking

**Effect:** Relevant documents ranked higher
- Before: 5 docs, 3 relevant (at rank 3-5) → rel = 3/25 = 0.12
- After: 5 docs, 4 relevant (at rank 1-3) → rel = 4/25 = 0.16

---

## Key Insight: Why Relevance ≠ Retrieval Accuracy

**v14 has:**
- Retrieval Accuracy: 95% (19/20 correct docs at rank 1)
- Relevance Score: 48.9%

**Why the difference?**

**Retrieval Accuracy** = Does the correct source document get retrieved?
- Answer: YES (95% of the time)

**Relevance Score** = Are the retrieved documents relevant to the query?
- Answer: PARTIALLY (only ~49% of retrieved sentences are relevant)

**Example:**
- Query: "Is diabetes a negative prognostic factor for NSCLC?"
- Correct source doc: Retrieved ✓ (rank 1)
- But also retrieved: 4 other docs about diabetes, lung cancer, prognosis, etc.
- Only 2 of the 5 docs are specifically about diabetes + NSCLC interaction
- Relevance: 2/5 = 40%

---

## The Relevance Paradox

**v14 achieves:**
- ✅ 95% retrieval accuracy (correct docs found)
- ✅ 85% adherence (answers follow passage-only rule)
- ✅ 68.5% completeness (uses all relevant docs)
- ❌ 48.9% relevance (only ~49% of retrieved docs are relevant)

**Why?**

The retrieval system is good at finding the correct source document, but it also retrieves 4 other documents that are only partially relevant. The LLM then has to figure out which parts of which documents are actually relevant to the query.

**Solution:** Improve the retrieval system to retrieve ONLY highly relevant documents, not just the correct source document.

---

## Calculation Details

### Step 1: Split Documents into Sentences
```python
doc_sentences = [
    [["d0s0", "Sentence 1 from doc 0"], ["d0s1", "Sentence 2 from doc 0"]],
    [["d1s0", "Sentence 1 from doc 1"], ["d1s1", "Sentence 2 from doc 1"]],
    ...
]
```

### Step 2: Split Response into Sentences
```python
resp_sentences = [
    ["a", "Sentence 1 from response"],
    ["b", "Sentence 2 from response"],
    ...
]
```

### Step 3: LLM Judges Relevance
```
LLM output:
{
  "all_relevant_sentence_keys": ["d0s0", "d0s1", "d1s0"],  # 3 relevant
  "all_utilized_sentence_keys": ["d0s0", "d1s0"],  # 2 utilized
  "overall_supported": true
}
```

### Step 4: Calculate Metrics
```python
total_doc_sentences = 5  # Total sentences across all docs
relevant_keys = {"d0s0", "d0s1", "d1s0"}  # 3 relevant
utilized_keys = {"d0s0", "d1s0"}  # 2 utilized

relevance_score = 3 / 5 = 0.60
utilization_score = 2 / 5 = 0.40
completeness_score = 2 / 3 = 0.67
adherence_score = true
```

---

## Why This Matters for v15+

### v15 (Semantic Similarity Threshold)
**Goal:** Improve relevance by filtering low-quality documents

**How it works:**
- Only retrieve documents with similarity > 0.5
- Fewer documents, but higher quality
- Expected: rel 0.489 → 0.510-0.530

**Why it helps:**
- Fewer irrelevant documents in the set
- Higher proportion of relevant sentences
- LLM has less noise to filter

### v16 (Multi-Stage Retrieval)
**Goal:** Improve relevance by better ranking

**How it works:**
- Retrieve with multiple embeddings
- Rerank with cross-encoder
- Put most relevant docs at top
- Expected: rel 0.489 → 0.560-0.600

**Why it helps:**
- Relevant documents ranked higher
- LLM focuses on top documents
- Better semantic matching

### v17 (Fine-Tuning)
**Goal:** Improve relevance by learning task-specific patterns

**How it works:**
- Fine-tune PubMedBERT on PubMedQA
- Learn what makes a document relevant to a query
- Expected: rel 0.489 → 0.650+

**Why it helps:**
- Embedding understands task-specific relevance
- Better matching between query and documents
- Fewer irrelevant documents retrieved

---

## Summary

| Aspect | Details |
|--------|---------|
| **What is measured** | Proportion of retrieved document sentences that are relevant to the query |
| **Calculation** | (Relevant sentences) / (Total sentences in all retrieved docs) |
| **Range** | 0.0 to 1.0 (0% to 100%) |
| **v14 value** | 0.489 (48.9%) |
| **Why low** | Retrieved docs contain many irrelevant sentences |
| **How to improve** | Better retrieval (filtering, ranking, embedding) |
| **Expected v15** | 0.510-0.530 (+4-8%) |
| **Expected v16** | 0.560-0.600 (+10-18%) |
| **Expected v17** | 0.650+ (+20-33%) |

---

## Generated: 2026-07-18
**Source:** `evaluation/strategies/trace/strategy.py:177`
