"""Analyze relevance issues and identify improvement opportunities."""
import json
import sys
from pathlib import Path

jsonl_path = sys.argv[1] if len(sys.argv) > 1 else 'rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl'

if not Path(jsonl_path).exists():
    print(f"Error: File not found at {jsonl_path}")
    sys.exit(1)

# Load JSONL data
results = []
with open(jsonl_path) as f:
    for line in f:
        results.append(json.loads(line))

print("=" * 100)
print("RELEVANCE IMPROVEMENT ANALYSIS")
print("=" * 100)

print("\n=== RELEVANCE DISTRIBUTION ===\n")

rel_ranges = {
    '0.0-0.2': [],
    '0.2-0.4': [],
    '0.4-0.6': [],
    '0.6-0.8': [],
    '0.8-1.0': []
}

for result in results:
    rel = result['metadata']['ground_truth']['relevance_score']
    query_idx = result['metadata']['query_index']
    query = result['query'][:60]
    
    if rel < 0.2:
        rel_ranges['0.0-0.2'].append((query_idx, rel, query))
    elif rel < 0.4:
        rel_ranges['0.2-0.4'].append((query_idx, rel, query))
    elif rel < 0.6:
        rel_ranges['0.4-0.6'].append((query_idx, rel, query))
    elif rel < 0.8:
        rel_ranges['0.6-0.8'].append((query_idx, rel, query))
    else:
        rel_ranges['0.8-1.0'].append((query_idx, rel, query))

for range_name, queries in rel_ranges.items():
    print(f"{range_name}: {len(queries)} queries")
    for q_idx, rel, query in sorted(queries, key=lambda x: x[1]):
        print(f"  Q{q_idx:02d}: rel={rel:.4f} | {query}")
    print()

print("\n=== PROBLEM QUERIES (rel < 0.4) ===\n")

problem_queries = []
for result in results:
    rel = result['metadata']['ground_truth']['relevance_score']
    if rel < 0.4:
        query_idx = result['metadata']['query_index']
        query = result['query']
        docs = result['retrieved_docs']
        answer = result['answer']
        
        problem_queries.append({
            'idx': query_idx,
            'rel': rel,
            'query': query,
            'docs': docs,
            'answer': answer
        })

for pq in sorted(problem_queries, key=lambda x: x['rel']):
    print(f"Q{pq['idx']:02d}: rel={pq['rel']:.4f}")
    print(f"Query: {pq['query']}")
    print(f"\nRetrieved Documents:")
    for i, doc in enumerate(pq['docs'][:3], 1):
        content = doc['content'][:100]
        sample_idx = doc['metadata']['sample_index']
        print(f"  Doc {i} (sample_{sample_idx}): {content}...")
    print(f"\nGenerated Answer: {pq['answer'][:150]}...")
    print("\n" + "-" * 100 + "\n")

print("\n=== ROOT CAUSE ANALYSIS ===\n")

# Categorize problems
issues = {
    'geographic_specificity': [],
    'niche_medical_topic': [],
    'recommendation_question': [],
    'complex_multi_faceted': [],
    'unclear_retrieval': []
}

# Q19: Metabolic disorders
issues['niche_medical_topic'].append({
    'query_idx': 19,
    'query': 'Can metabolic disorders in aging men contribute to prostatic hyperplasia eligible for TURP?',
    'issue': 'Very specific medical topic (metabolic syndrome + BPH)',
    'rel': 0.1111,
    'root_cause': 'PubMedBERT may not have enough training data on this specific combination'
})

# Q17: TB data
issues['geographic_specificity'].append({
    'query_idx': 17,
    'query': 'Are the statistical data from Benin\'s National Tuberculosis Programme reliable?',
    'issue': 'Geographic specificity (Benin) + data reliability question',
    'rel': 0.1667,
    'root_cause': 'Location-specific data not well captured in embedding space'
})

# Q11: Breast milk
issues['niche_medical_topic'].append({
    'query_idx': 11,
    'query': 'Comparison of creamatocrit and protein concentration in each mammary lobe',
    'issue': 'Very specific lactation/breast milk composition topic',
    'rel': 0.2500,
    'root_cause': 'Highly specialized topic, limited training data'
})

# Q14: Mixed chimerism
issues['niche_medical_topic'].append({
    'query_idx': 14,
    'query': 'Increasing mixed chimerism in acute lymphoblastic leukemia',
    'issue': 'Very specific hematology topic',
    'rel': 0.2500,
    'root_cause': 'Specialized oncology/hematology topic'
})

# Q02: Diabetes prognosis
issues['complex_multi_faceted'].append({
    'query_idx': 2,
    'query': 'Is diabetes mellitus a negative prognostic factor for NSCLC treatment?',
    'issue': 'Requires understanding of diabetes + lung cancer interaction',
    'rel': 0.2857,
    'root_cause': 'Multi-domain query (endocrinology + oncology)'
})

# Q12: Breast cancer
issues['unclear_retrieval'].append({
    'query_idx': 12,
    'query': 'Do T1a breast cancers profit from adjuvant systemic therapy?',
    'issue': 'Retrieved docs discuss adjuvant therapy but not specifically T1a',
    'rel': 0.3077,
    'root_cause': 'Query specificity (T1a stage) not well matched'
})

# Q07: Clopidogrel
issues['complex_multi_faceted'].append({
    'query_idx': 7,
    'query': 'Platelet aggregation by BMI in coronary stenting: weight-adjusted clopidogrel?',
    'issue': 'Requires understanding of BMI + platelet response + drug dosing',
    'rel': 0.3750,
    'root_cause': 'Multi-domain query (cardiology + pharmacology + statistics)'
})

for category, queries in issues.items():
    if queries:
        print(f"{category.upper().replace('_', ' ')}:")
        for q in queries:
            print(f"  Q{q['query_idx']:02d}: rel={q['rel']:.4f}")
            print(f"    Query: {q['query'][:80]}...")
            print(f"    Root Cause: {q['root_cause']}")
        print()

print("\n=== IMPROVEMENT STRATEGIES ===\n")

strategies = {
    'Strategy 1: Hybrid Embedding (Dense + Sparse)': {
        'description': 'Combine PubMedBERT (semantic) with BM25 (keyword)',
        'impact_on_relevance': '+5-10%',
        'effort': 'Medium',
        'best_for': ['Q02', 'Q07', 'Q12'],
        'why': 'Captures both semantic meaning and exact terminology'
    },
    'Strategy 2: Query Expansion with Medical Ontologies': {
        'description': 'Expand queries using UMLS/MeSH medical ontologies',
        'impact_on_relevance': '+8-15%',
        'effort': 'High',
        'best_for': ['Q19', 'Q11', 'Q14'],
        'why': 'Maps medical terms to standard vocabularies'
    },
    'Strategy 3: Fine-tuned Biomedical Embedding': {
        'description': 'Fine-tune PubMedBERT on PubMedQA dataset',
        'impact_on_relevance': '+10-20%',
        'effort': 'Very High',
        'best_for': ['Q19', 'Q11', 'Q14', 'Q02'],
        'why': 'Learns task-specific relevance patterns'
    },
    'Strategy 4: Multi-Stage Retrieval': {
        'description': 'Retrieve with multiple embeddings, rerank with cross-encoder',
        'impact_on_relevance': '+5-12%',
        'effort': 'High',
        'best_for': ['Q02', 'Q07', 'Q12', 'Q17'],
        'why': 'Captures different aspects of relevance'
    },
    'Strategy 5: Query Rewriting for Clarity': {
        'description': 'Rewrite complex queries to simpler, more specific forms',
        'impact_on_relevance': '+3-8%',
        'effort': 'Low',
        'best_for': ['Q02', 'Q07'],
        'why': 'Makes queries easier to match against documents'
    },
    'Strategy 6: Semantic Similarity Threshold': {
        'description': 'Filter retrieved docs by minimum similarity score',
        'impact_on_relevance': '+2-5%',
        'effort': 'Low',
        'best_for': ['All queries'],
        'why': 'Removes low-quality matches'
    },
    'Strategy 7: Location-Aware Retrieval': {
        'description': 'Add geographic context to retrieval',
        'impact_on_relevance': '+10-20%',
        'effort': 'High',
        'best_for': ['Q17'],
        'why': 'Specifically targets geographic specificity issue'
    },
    'Strategy 8: Specialized Domain Embeddings': {
        'description': 'Use specialized embeddings for specific domains',
        'impact_on_relevance': '+8-15%',
        'effort': 'Very High',
        'best_for': ['Q19', 'Q11', 'Q14'],
        'why': 'Optimized for specific medical domains'
    }
}

for strategy_name, details in strategies.items():
    print(f"{strategy_name}")
    print(f"  Description: {details['description']}")
    print(f"  Expected Impact: {details['impact_on_relevance']}")
    print(f"  Effort: {details['effort']}")
    print(f"  Best For: {', '.join(details['best_for'])}")
    print(f"  Why: {details['why']}")
    print()

print("\n=== RECOMMENDED APPROACH ===\n")

print("QUICK WINS (Low Effort, Medium Impact):")
print("1. Add semantic similarity threshold (min 0.5)")
print("   - Expected: +2-5% relevance")
print("   - Effort: 1 hour")
print("   - Implementation: Add to retrieval config")
print()

print("2. Implement query rewriting for complex queries")
print("   - Expected: +3-8% relevance")
print("   - Effort: 2-3 hours")
print("   - Implementation: Pre-process step before retrieval")
print()

print("MEDIUM EFFORT (High Impact):")
print("3. Implement multi-stage retrieval with cross-encoder reranking")
print("   - Expected: +5-12% relevance")
print("   - Effort: 4-6 hours")
print("   - Implementation: Add second reranking stage")
print()

print("4. Query expansion with medical ontologies (UMLS/MeSH)")
print("   - Expected: +8-15% relevance")
print("   - Effort: 6-8 hours")
print("   - Implementation: Integrate UMLS API or local database")
print()

print("HIGH EFFORT (Highest Impact):")
print("5. Fine-tune PubMedBERT on PubMedQA dataset")
print("   - Expected: +10-20% relevance")
print("   - Effort: 16-24 hours")
print("   - Implementation: Training pipeline with GPU")
print()

print("\n=== EXPECTED RESULTS ===\n")

print("Current v14: rel=0.489")
print()
print("After Quick Wins (1+2):        rel=0.510-0.530 (+4-8%)")
print("After Medium Effort (3+4):     rel=0.540-0.580 (+10-18%)")
print("After High Effort (5):         rel=0.590-0.650 (+20-33%)")
print()

print("\n=== NEXT STEPS ===\n")

print("1. IMMEDIATE (v15):")
print("   - Add semantic similarity threshold")
print("   - Implement query rewriting for complex queries")
print("   - Expected: rel 0.489 → 0.510-0.530")
print()

print("2. SHORT-TERM (v16):")
print("   - Implement multi-stage retrieval")
print("   - Add query expansion with medical ontologies")
print("   - Expected: rel 0.530 → 0.560-0.600")
print()

print("3. LONG-TERM (v17):")
print("   - Fine-tune PubMedBERT on PubMedQA")
print("   - Expected: rel 0.600 → 0.650+")
print()

print("=" * 100)
