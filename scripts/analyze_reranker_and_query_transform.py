"""Analyze reranker and query transform options for v15."""
import json
from pathlib import Path

print("=" * 100)
print("RERANKER & QUERY TRANSFORM ANALYSIS FOR v15")
print("=" * 100)

print("\n=== CURRENT v14 SETUP ===\n")

print("Reranker:")
print("  Model: BAAI/bge-reranker-v2-m3")
print("  Type: General-purpose cross-encoder")
print("  Training: Trained on general web data")
print("  Pros: Fast, reliable, widely used")
print("  Cons: Not optimized for biomedical domain")
print()

print("Query Transform:")
print("  Type: step_back")
print("  Strategy: Breaks complex queries into sub-questions")
print("  Pros: Excellent for complex queries (Q10 +492%)")
print("  Cons: More API calls, slower")
print()

print("\n=== RERANKER OPTIONS ===\n")

rerankers = {
    'BAAI/bge-reranker-v2-m3': {
        'name': 'BGE Reranker v2-m3 (Current)',
        'type': 'General-purpose cross-encoder',
        'training_data': 'Web data',
        'domain': 'General',
        'model_size': 'Medium (335M)',
        'speed': 'Fast',
        'accuracy': 'Good',
        'biomedical_optimized': False,
        'pros': [
            'Fast inference',
            'Widely used and tested',
            'Good general-purpose performance',
            'Supports multiple languages'
        ],
        'cons': [
            'Not optimized for biomedical domain',
            'May miss medical terminology nuances',
            'Lower relevance for specialized queries'
        ],
        'expected_improvement': 'Baseline (0%)',
        'effort': 'None (already in use)',
        'availability': 'Public (HuggingFace)'
    },
    
    'BAAI/bge-reranker-large': {
        'name': 'BGE Reranker Large',
        'type': 'General-purpose cross-encoder',
        'training_data': 'Web data',
        'domain': 'General',
        'model_size': 'Large (560M)',
        'speed': 'Medium',
        'accuracy': 'Very Good',
        'biomedical_optimized': False,
        'pros': [
            'Better accuracy than v2-m3',
            'Larger model captures more nuance',
            'Still reasonably fast',
            'Public model'
        ],
        'cons': [
            'Slower than v2-m3',
            'Still not biomedical-specific',
            'Larger memory footprint'
        ],
        'expected_improvement': '+2-3% relevance',
        'effort': '1 hour (config change)',
        'availability': 'Public (HuggingFace)'
    },
    
    'cross-encoder/ms-marco-MiniLM-L-12-v2': {
        'name': 'MS MARCO MiniLM',
        'type': 'Cross-encoder',
        'training_data': 'MS MARCO dataset (web search)',
        'domain': 'General',
        'model_size': 'Small (33M)',
        'speed': 'Very Fast',
        'accuracy': 'Good',
        'biomedical_optimized': False,
        'pros': [
            'Very fast inference',
            'Small model size',
            'Good for web search',
            'Public model'
        ],
        'cons': [
            'Smaller model, less nuanced',
            'Not biomedical-specific',
            'Lower accuracy than BGE'
        ],
        'expected_improvement': '-1-2% relevance (worse)',
        'effort': '1 hour (config change)',
        'availability': 'Public (HuggingFace)'
    },
    
    'allenai/specter': {
        'name': 'SPECTER (Scientific Paper Embeddings)',
        'type': 'Embedding model (not reranker)',
        'training_data': 'Scientific papers (S2ORC)',
        'domain': 'Scientific/Academic',
        'model_size': 'Medium (310M)',
        'speed': 'Medium',
        'accuracy': 'Very Good for scientific papers',
        'biomedical_optimized': True,
        'pros': [
            'Trained on scientific papers',
            'Understands academic language',
            'Good for biomedical papers',
            'Public model'
        ],
        'cons': [
            'Not a reranker (embedding model)',
            'Would need to replace embedding, not reranker',
            'Different architecture'
        ],
        'expected_improvement': '+5-10% relevance (if used as embedding)',
        'effort': 'Medium (replace embedding model)',
        'availability': 'Public (HuggingFace)'
    },
    
    'cross-encoder/qnli-distilroberta-base': {
        'name': 'DistilRoBERTa QNLI',
        'type': 'Cross-encoder',
        'training_data': 'QNLI dataset',
        'domain': 'General Q&A',
        'model_size': 'Small (82M)',
        'speed': 'Fast',
        'accuracy': 'Good',
        'biomedical_optimized': False,
        'pros': [
            'Trained on Q&A data',
            'Understands question-answer relevance',
            'Small and fast',
            'Public model'
        ],
        'cons': [
            'Not biomedical-specific',
            'Smaller model',
            'General Q&A focused'
        ],
        'expected_improvement': '+1-2% relevance',
        'effort': '1 hour (config change)',
        'availability': 'Public (HuggingFace)'
    },
    
    'sentence-transformers/pubmedbert-base-uncased-mnli': {
        'name': 'PubMedBERT MNLI (Biomedical)',
        'type': 'Cross-encoder (MNLI-based)',
        'training_data': 'PubMed + MNLI',
        'domain': 'Biomedical',
        'model_size': 'Medium (110M)',
        'speed': 'Fast',
        'accuracy': 'Excellent for biomedical',
        'biomedical_optimized': True,
        'pros': [
            'Trained on PubMed data',
            'Understands biomedical terminology',
            'MNLI training for relevance',
            'Fast inference',
            'Public model',
            '⭐ BEST FOR PUBMEDQA'
        ],
        'cons': [
            'Smaller than BGE',
            'Less general-purpose'
        ],
        'expected_improvement': '+5-10% relevance ⭐',
        'effort': '1 hour (config change)',
        'availability': 'Public (HuggingFace)'
    },
    
    'sentence-transformers/nli-deberta-v3-large': {
        'name': 'DeBERTa v3 Large NLI',
        'type': 'Cross-encoder',
        'training_data': 'NLI datasets',
        'domain': 'General',
        'model_size': 'Large (435M)',
        'speed': 'Medium',
        'accuracy': 'Excellent',
        'biomedical_optimized': False,
        'pros': [
            'State-of-the-art NLI performance',
            'Large model, very accurate',
            'Good for relevance ranking',
            'Public model'
        ],
        'cons': [
            'Not biomedical-specific',
            'Slower inference',
            'Larger memory footprint'
        ],
        'expected_improvement': '+3-5% relevance',
        'effort': '1 hour (config change)',
        'availability': 'Public (HuggingFace)'
    }
}

for model_name, details in rerankers.items():
    print(f"{details['name']}")
    print(f"  Model: {model_name}")
    print(f"  Type: {details['type']}")
    print(f"  Domain: {details['domain']}")
    print(f"  Size: {details['model_size']}")
    print(f"  Speed: {details['speed']}")
    print(f"  Biomedical: {'✅ YES' if details['biomedical_optimized'] else '❌ NO'}")
    print(f"  Expected Impact: {details['expected_improvement']}")
    print(f"  Effort: {details['effort']}")
    print(f"  Pros:")
    for pro in details['pros']:
        print(f"    ✓ {pro}")
    print(f"  Cons:")
    for con in details['cons']:
        print(f"    ✗ {con}")
    print()

print("\n=== RERANKER RECOMMENDATION ===\n")

print("🏆 BEST CHOICE: sentence-transformers/pubmedbert-base-uncased-mnli")
print()
print("Why:")
print("  1. Trained on PubMed data (biomedical-specific)")
print("  2. MNLI training for relevance ranking")
print("  3. Fast inference (110M parameters)")
print("  4. Expected +5-10% relevance improvement")
print("  5. Only 1 hour to implement")
print("  6. Public model, no training needed")
print()

print("\n=== QUERY TRANSFORM OPTIONS ===\n")

query_transforms = {
    'step_back': {
        'name': 'Step-Back Query Transform (Current)',
        'description': 'Breaks complex queries into simpler sub-questions',
        'how_it_works': [
            '1. Takes original query',
            '2. Generates simpler, more fundamental sub-questions',
            '3. Retrieves for each sub-question',
            '4. Combines results'
        ],
        'api_calls': 'N+1 (1 for step-back, N for retrieval)',
        'latency': 'Slower (extra LLM call)',
        'best_for': ['Complex queries', 'Multi-faceted questions', 'Nuanced queries'],
        'v14_results': [
            'Q03 (Elderly fluids): +169% relevance',
            'Q06 (Disability): +239% relevance',
            'Q10 (Surgery/RT): +492% relevance',
            'Q07 (Clopidogrel): +50% relevance'
        ],
        'pros': [
            'Excellent for complex queries',
            'Breaks down multi-faceted questions',
            'Better query understanding',
            'Proven results in v14'
        ],
        'cons': [
            'More API calls',
            'Slower latency',
            'May over-complicate simple queries'
        ],
        'expected_improvement': 'Already in v14 (+24% utilization)',
        'effort': 'None (already implemented)'
    },
    
    'multi_query': {
        'name': 'Multi-Query Transform',
        'description': 'Generates multiple variations of the query',
        'how_it_works': [
            '1. Takes original query',
            '2. Generates N variations (e.g., 5)',
            '3. Retrieves for each variation',
            '4. Combines and deduplicates results'
        ],
        'api_calls': 'N+1 (1 for generation, N for retrieval)',
        'latency': 'Slower (extra LLM call)',
        'best_for': ['Simple queries', 'Keyword variations', 'Synonym coverage'],
        'v13_results': [
            'v13 used multi_query (5 queries, 0.5 temp)',
            'Completeness: 0.632 (good)',
            'Utilization: 0.324 (moderate)',
            'Relevance: 0.508 (moderate)'
        ],
        'pros': [
            'Captures keyword variations',
            'Good for simple queries',
            'Covers different phrasings',
            'Simpler than step-back'
        ],
        'cons': [
            'May generate redundant queries',
            'Less effective for complex queries',
            'More API calls than step-back'
        ],
        'expected_improvement': '+2-5% relevance (vs step-back)',
        'effort': '2 hours (implement + test)'
    },
    
    'hybrid': {
        'name': 'Hybrid: Step-Back + Multi-Query',
        'description': 'Combines both strategies',
        'how_it_works': [
            '1. Step-back generates sub-questions',
            '2. For each sub-question, generate variations',
            '3. Retrieve for all queries',
            '4. Combine and deduplicate'
        ],
        'api_calls': 'N*M+1 (many API calls)',
        'latency': 'Much slower',
        'best_for': ['Very complex queries', 'Maximum coverage'],
        'v14_results': [
            'Not tested yet',
            'Theoretically best coverage'
        ],
        'pros': [
            'Maximum query coverage',
            'Handles all query types',
            'Best for edge cases'
        ],
        'cons': [
            'Many API calls (expensive)',
            'Much slower latency',
            'Overkill for simple queries',
            'May retrieve too many docs'
        ],
        'expected_improvement': '+3-8% relevance',
        'effort': '4-6 hours (implement + test)'
    },
    
    'query_rewriter': {
        'name': 'Query Rewriter',
        'description': 'Rewrites query to be clearer and more specific',
        'how_it_works': [
            '1. Takes original query',
            '2. Rewrites to be clearer',
            '3. Breaks down complex parts',
            '4. Retrieves with rewritten query'
        ],
        'api_calls': '2 (1 for rewriting, 1 for retrieval)',
        'latency': 'Slightly slower',
        'best_for': ['Complex queries', 'Ambiguous queries', 'Multi-domain queries'],
        'v14_results': [
            'Not tested yet',
            'Expected to help Q02, Q07'
        ],
        'pros': [
            'Simplifies complex queries',
            'Fewer API calls than multi_query',
            'Better for multi-domain queries',
            'Improves query clarity'
        ],
        'cons': [
            'May lose original query intent',
            'Requires careful prompt engineering',
            'Not tested yet'
        ],
        'expected_improvement': '+3-8% relevance',
        'effort': '2-3 hours (implement + test)'
    }
}

for transform_name, details in query_transforms.items():
    print(f"{details['name']}")
    print(f"  Description: {details['description']}")
    print(f"  API Calls: {details['api_calls']}")
    print(f"  Latency: {details['latency']}")
    print(f"  Best For: {', '.join(details['best_for'])}")
    print(f"  Expected Impact: {details['expected_improvement']}")
    print(f"  Effort: {details['effort']}")
    print(f"  Pros:")
    for pro in details['pros']:
        print(f"    ✓ {pro}")
    print(f"  Cons:")
    for con in details['cons']:
        print(f"    ✗ {con}")
    print()

print("\n=== QUERY TRANSFORM RECOMMENDATION ===\n")

print("🏆 BEST CHOICE: Keep step-back (already in v14)")
print()
print("Why:")
print("  1. Already proven in v14 (+24% utilization)")
print("  2. Excellent for complex queries (Q10 +492%)")
print("  3. No additional implementation needed")
print("  4. Works well with biomedical queries")
print()

print("⭐ OPTIONAL: Add multi_query as fallback")
print()
print("Why:")
print("  1. Captures keyword variations")
print("  2. Helps simple queries")
print("  3. Can be combined with step-back")
print("  4. Expected +2-5% additional improvement")
print()

print("\n=== v15 RECOMMENDED CONFIGURATION ===\n")

print("Changes from v14:")
print()
print("1. RERANKER UPGRADE (1 hour)")
print("   From: BAAI/bge-reranker-v2-m3 (general)")
print("   To:   sentence-transformers/pubmedbert-base-uncased-mnli (biomedical)")
print("   Expected Impact: +5-10% relevance")
print()

print("2. QUERY TRANSFORM (OPTIONAL, 2 hours)")
print("   Option A: Keep step-back only (current)")
print("   Option B: Add multi_query as fallback")
print("   Expected Impact: +2-5% additional relevance")
print()

print("3. SEMANTIC SIMILARITY THRESHOLD (1 hour)")
print("   Add: min_similarity: 0.5")
print("   Expected Impact: +2-5% relevance")
print()

print("TOTAL EFFORT: 2-4 hours")
print("TOTAL EXPECTED IMPROVEMENT: +9-20% relevance")
print("NEW EXPECTED RELEVANCE: 0.489 → 0.535-0.585")
print()

print("\n=== IMPLEMENTATION PLAN ===\n")

print("Step 1: Update reranker (1 hour)")
print("  - Change model_name in config")
print("  - Test on 5 queries")
print()

print("Step 2: Add semantic similarity threshold (1 hour)")
print("  - Add min_similarity: 0.5 to dense search config")
print("  - Test on 5 queries")
print()

print("Step 3: (OPTIONAL) Add multi_query fallback (2 hours)")
print("  - Implement hybrid query transform")
print("  - Step-back for complex queries")
print("  - Multi-query for simple queries")
print("  - Test on all 20 queries")
print()

print("Step 4: Run full v15 experiment")
print("  - Run on all 20 queries")
print("  - Compare against v14")
print("  - Analyze improvements")
print()

print("\n=== EXPECTED v15 RESULTS ===\n")

print("Metric         | v14    | v15 Expected | Change")
print("---------------|--------|--------------|--------")
print("Relevance      | 0.489  | 0.535-0.585  | +9-20%")
print("Adherence      | 0.850  | 0.850        | No change")
print("Completeness   | 0.685  | 0.685-0.700  | Maintained")
print("Utilization    | 0.370  | 0.380-0.400  | +3-8%")
print()

print("=" * 100)
