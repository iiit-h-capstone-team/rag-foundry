# Relevance Score Improvement Guide

## Current State

**v14 Relevance:** 0.489 (48.9%)

**Problem Queries (rel < 0.4):** 7 out of 20 queries
- Q19: 0.1111 (Metabolic disorders)
- Q17: 0.1667 (TB data)
- Q11: 0.2500 (Breast milk)
- Q14: 0.2500 (Mixed chimerism)
- Q02: 0.2857 (Diabetes prognosis)
- Q12: 0.3077 (Breast cancer)
- Q07: 0.3750 (Clopidogrel dosing)

---

## Root Causes

### 1. Niche Medical Topics (Q19, Q11, Q14)
**Problem:** Very specific medical domains with limited training data
- Q19: Metabolic syndrome + benign prostatic hyperplasia (BPH)
- Q11: Lactation science + creamatocrit analysis
- Q14: Hematology + mixed chimerism in leukemia

**Why PubMedBERT struggles:**
- These are highly specialized topics
- Limited overlap with general biomedical text
- Requires domain-specific knowledge

**Solution:** Fine-tuning or specialized embeddings

### 2. Geographic Specificity (Q17)
**Problem:** Location-specific data (Benin's TB program)
- Query: "Are the statistical data from Benin's National Tuberculosis Programme reliable?"
- Issue: Geographic context not captured in embedding space

**Why PubMedBERT struggles:**
- Embeddings don't encode geographic information
- Location-specific data is sparse in training data

**Solution:** Location-aware retrieval or query expansion

### 3. Complex Multi-Faceted Queries (Q02, Q07)
**Problem:** Requires understanding multiple domains
- Q02: Diabetes (endocrinology) + NSCLC (oncology)
- Q07: BMI (statistics) + platelet response (hematology) + drug dosing (pharmacology)

**Why PubMedBERT struggles:**
- Single embedding can't capture all aspects
- Requires cross-domain reasoning

**Solution:** Query rewriting or multi-stage retrieval

### 4. Query Specificity Mismatch (Q12)
**Problem:** Query mentions specific stage (T1a) not well matched
- Query: "Do T1a breast cancers profit from adjuvant systemic therapy?"
- Retrieved docs discuss adjuvant therapy but not specifically T1a stage

**Why PubMedBERT struggles:**
- Stage-specific information is fine-grained
- Embedding may not distinguish T1a from T1b or T2

**Solution:** Better query expansion or semantic similarity filtering

---

## Improvement Strategies

### Strategy 1: Semantic Similarity Threshold ⭐ QUICK WIN

**What:** Filter retrieved documents by minimum similarity score

**Implementation:**
```yaml
retrieval:
  search:
    searches:
      - type: dense
        config:
          top_k: 75
          context_window: 2
          min_similarity: 0.5  # NEW: Filter low-quality matches
```

**Expected Impact:** +2-5% relevance (0.489 → 0.510-0.515)

**Why it works:**
- Removes documents with low semantic similarity
- Prevents noisy documents from confusing the model
- Improves relevance scoring

**Effort:** 1 hour

**Best for:** All queries, especially Q02, Q07, Q12

---

### Strategy 2: Query Rewriting for Clarity ⭐ QUICK WIN

**What:** Rewrite complex queries to simpler, more specific forms

**Implementation:**
```yaml
retrieval:
  query_transform:
    type: query_rewriter  # NEW: Rewrite before step-back
    config:
      model: llama-3.3-70b-versatile
      temperature: 0.3
      system_prompt: |
        Rewrite the query to be clearer and more specific.
        Break down complex queries into simpler components.
        Preserve all important details.
```

**Expected Impact:** +3-8% relevance (0.489 → 0.520-0.530)

**Why it works:**
- Simplifies complex queries
- Makes them easier to match against documents
- Breaks down multi-domain queries

**Effort:** 2-3 hours

**Best for:** Q02, Q07 (complex multi-faceted)

**Examples:**
- Q02 Original: "Is diabetes mellitus a negative prognostic factor for the treatment of advanced non-small-cell lung cancer?"
- Q02 Rewritten: "Does diabetes affect survival in NSCLC patients? What is the prognostic significance of diabetes in lung cancer treatment?"

- Q07 Original: "Platelet aggregation according to body mass index in patients undergoing coronary stenting: should clopidogrel loading-dose be weight adjusted?"
- Q07 Rewritten: "Does body mass index affect platelet response to clopidogrel? Should clopidogrel dose be adjusted for weight?"

---

### Strategy 3: Multi-Stage Retrieval 🎯 MEDIUM EFFORT

**What:** Retrieve with multiple embeddings, rerank with cross-encoder

**Implementation:**
```yaml
retrieval:
  search:
    searches:
      - type: dense
        config:
          model: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
          top_k: 75
      - type: dense
        config:
          model: BAAI/bge-large-en-v1.5  # NEW: Second embedding
          top_k: 75
      - type: sparse
        config:
          top_k: 75
  
  fusion:
    type: weighted_sum
    config:
      dense_weight: 0.5
      dense_weight_2: 0.2
      sparse_weight: 0.3
  
  rerank:
    type: cross_encoder
    config:
      model_name: BAAI/bge-reranker-v2-m3
      top_k: 20  # Increased from 15
```

**Expected Impact:** +5-12% relevance (0.489 → 0.540-0.570)

**Why it works:**
- PubMedBERT captures biomedical semantics
- BGE captures general semantic meaning
- Cross-encoder reranker combines both perspectives
- Captures different aspects of relevance

**Effort:** 4-6 hours

**Best for:** Q02, Q07, Q12, Q17

---

### Strategy 4: Query Expansion with Medical Ontologies 🎯 MEDIUM EFFORT

**What:** Expand queries using UMLS/MeSH medical ontologies

**Implementation:**
```python
# Pseudo-code
from umls_client import UMLSClient

def expand_query(query):
    # Extract medical terms
    terms = extract_medical_terms(query)
    
    # Get synonyms and related terms from UMLS
    expanded_terms = []
    for term in terms:
        synonyms = umls_client.get_synonyms(term)
        related = umls_client.get_related_concepts(term)
        expanded_terms.extend(synonyms + related)
    
    # Create expanded query
    return query + " " + " ".join(expanded_terms)
```

**Expected Impact:** +8-15% relevance (0.489 → 0.560-0.600)

**Why it works:**
- Maps medical terms to standard vocabularies
- Captures synonyms and related concepts
- Improves matching with medical literature

**Effort:** 6-8 hours

**Best for:** Q19, Q11, Q14 (niche medical topics)

**Examples:**
- Q19 Original: "Can metabolic disorders in aging men contribute to prostatic hyperplasia eligible for TURP?"
- Q19 Expanded: "Can metabolic syndrome, diabetes, obesity in elderly males contribute to benign prostatic hyperplasia (BPH) eligible for transurethral resection of prostate?"

---

### Strategy 5: Fine-tuned Biomedical Embedding 🚀 HIGH EFFORT

**What:** Fine-tune PubMedBERT on PubMedQA dataset

**Implementation:**
```python
# Training pipeline
from transformers import AutoModel, AutoTokenizer
import torch

# Load PubMedBERT
model = AutoModel.from_pretrained('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')
tokenizer = AutoTokenizer.from_pretrained('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')

# Fine-tune on PubMedQA
# 1. Create training pairs: (query, relevant_doc, irrelevant_doc)
# 2. Use contrastive loss to learn relevance
# 3. Train for 3-5 epochs
# 4. Evaluate on validation set
```

**Expected Impact:** +10-20% relevance (0.489 → 0.590-0.650)

**Why it works:**
- Learns task-specific relevance patterns
- Understands what makes a document relevant to a query
- Optimized for PubMedQA task

**Effort:** 16-24 hours (requires GPU)

**Best for:** Q19, Q11, Q14, Q02 (all problem queries)

**Requirements:**
- GPU (NVIDIA A100 or similar)
- Training data (PubMedQA queries + relevant/irrelevant docs)
- 2-3 hours training time

---

### Strategy 6: Specialized Domain Embeddings 🚀 HIGH EFFORT

**What:** Use specialized embeddings for specific medical domains

**Implementation:**
```yaml
# For niche queries, use specialized embeddings
retrieval:
  search:
    searches:
      - type: dense
        config:
          model: microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext
          top_k: 50
      - type: dense
        config:
          model: oncology_specialized_embedding  # For Q14, Q19
          top_k: 25
          condition: query_contains(['leukemia', 'cancer', 'oncology'])
```

**Expected Impact:** +8-15% relevance (0.489 → 0.560-0.600)

**Why it works:**
- Optimized for specific medical domains
- Better understanding of domain-specific terminology
- Captures domain-specific relationships

**Effort:** Very High (requires finding/training specialized models)

**Best for:** Q19, Q11, Q14

---

### Strategy 7: Location-Aware Retrieval 🎯 MEDIUM EFFORT

**What:** Add geographic context to retrieval

**Implementation:**
```python
def location_aware_retrieval(query):
    # Extract location from query
    location = extract_location(query)  # "Benin"
    
    # Boost documents mentioning location
    results = retrieve(query)
    
    if location:
        for doc in results:
            if location.lower() in doc['content'].lower():
                doc['score'] *= 1.5  # Boost location-specific docs
    
    return sorted(results, key=lambda x: x['score'], reverse=True)
```

**Expected Impact:** +10-20% relevance for Q17 (0.167 → 0.300-0.400)

**Why it works:**
- Prioritizes location-specific documents
- Captures geographic context
- Improves matching for location-specific queries

**Effort:** 4-6 hours

**Best for:** Q17 (geographic specificity)

---

## Recommended Roadmap

### Phase 1: Quick Wins (v15) - 3-4 hours
**Goal:** rel 0.489 → 0.510-0.530

1. Add semantic similarity threshold (min 0.5)
2. Implement query rewriting for complex queries

**Implementation:**
- Update `pubmedqa_v14_pubmedbert_stepback.yaml` to add min_similarity
- Create query rewriter module
- Test on 20 queries

---

### Phase 2: Medium Effort (v16) - 10-14 hours
**Goal:** rel 0.510-0.530 → 0.560-0.600

1. Implement multi-stage retrieval
2. Add query expansion with medical ontologies

**Implementation:**
- Add second embedding model (BGE)
- Integrate UMLS API or local database
- Update fusion strategy
- Test on 20 queries

---

### Phase 3: High Effort (v17) - 16-24 hours
**Goal:** rel 0.560-0.600 → 0.650+

1. Fine-tune PubMedBERT on PubMedQA
2. Optional: Specialized domain embeddings

**Implementation:**
- Create training pipeline
- Prepare training data
- Train on GPU
- Evaluate and deploy

---

## Expected Results

| Version | Relevance | Adherence | Completeness | Utilization | Status |
|---------|-----------|-----------|--------------|-------------|--------|
| v14 | 0.489 | 0.850 | 0.685 | 0.370 | Current |
| v15 | 0.510-0.530 | 0.850 | 0.685 | 0.370 | +4-8% |
| v16 | 0.560-0.600 | 0.850 | 0.685 | 0.370 | +10-18% |
| v17 | 0.650+ | 0.850 | 0.685 | 0.370 | +20-33% |

---

## Problem Query Improvements

### Q19 (Metabolic disorders): 0.1111 → ?
- v15: 0.1111 (no improvement expected)
- v16: 0.200-0.250 (query expansion helps)
- v17: 0.300-0.400 (fine-tuning helps)

### Q17 (TB data): 0.1667 → ?
- v15: 0.1667 (no improvement expected)
- v16: 0.250-0.350 (location-aware retrieval helps)
- v17: 0.350-0.450 (fine-tuning helps)

### Q11 (Breast milk): 0.2500 → ?
- v15: 0.2500 (no improvement expected)
- v16: 0.350-0.400 (query expansion helps)
- v17: 0.450-0.550 (fine-tuning helps)

### Q14 (Mixed chimerism): 0.2500 → ?
- v15: 0.2500 (no improvement expected)
- v16: 0.350-0.400 (query expansion helps)
- v17: 0.450-0.550 (fine-tuning helps)

### Q02 (Diabetes prognosis): 0.2857 → ?
- v15: 0.350-0.400 (query rewriting helps)
- v16: 0.450-0.500 (multi-stage retrieval helps)
- v17: 0.550-0.650 (fine-tuning helps)

### Q12 (Breast cancer): 0.3077 → ?
- v15: 0.350-0.400 (query rewriting helps)
- v16: 0.450-0.500 (multi-stage retrieval helps)
- v17: 0.550-0.650 (fine-tuning helps)

### Q07 (Clopidogrel): 0.3750 → ?
- v15: 0.450-0.500 (query rewriting helps)
- v16: 0.550-0.600 (multi-stage retrieval helps)
- v17: 0.650-0.750 (fine-tuning helps)

---

## Decision Matrix

| Strategy | Impact | Effort | Best For | Recommendation |
|----------|--------|--------|----------|-----------------|
| Semantic Similarity Threshold | Low (+2-5%) | Low (1h) | All | ✅ DO FIRST |
| Query Rewriting | Medium (+3-8%) | Low (2-3h) | Q02, Q07 | ✅ DO FIRST |
| Multi-Stage Retrieval | Medium (+5-12%) | High (4-6h) | Q02, Q07, Q12, Q17 | ✅ DO SECOND |
| Query Expansion (UMLS) | High (+8-15%) | High (6-8h) | Q19, Q11, Q14 | ✅ DO SECOND |
| Fine-tuning | Very High (+10-20%) | Very High (16-24h) | All | ✅ DO LAST |
| Specialized Embeddings | High (+8-15%) | Very High | Q19, Q11, Q14 | ⚠️ OPTIONAL |
| Location-Aware Retrieval | High (+10-20% for Q17) | Medium (4-6h) | Q17 | ✅ DO SECOND |

---

## Conclusion

**Yes, relevance can be improved from 0.489 to 0.650+** through a combination of strategies:

1. **Quick wins** (v15): +4-8% with minimal effort
2. **Medium effort** (v16): +10-18% with moderate effort
3. **High effort** (v17): +20-33% with significant effort

**Recommended approach:** Start with v15 (quick wins), then v16 (medium effort), then v17 (fine-tuning) based on time and resources available.

---

## Generated: 2026-07-18
**Analysis Tool:** `scripts/analyze_relevance_issues.py`
