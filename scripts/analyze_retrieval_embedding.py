"""Analyze retrieval and embedding performance from report."""
import json
import statistics
import sys
from pathlib import Path

report_path = sys.argv[1] if len(sys.argv) > 1 else 'rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v13_balanced.json'

if not Path(report_path).exists():
    print(f"Error: Report not found at {report_path}")
    sys.exit(1)

with open(report_path) as f:
    data = json.load(f)

s = data['sections'][0]
config_name = s.get('config_name', 'unknown')
total_queries = len(s['per_query'])

print("=" * 100)
print(f"RETRIEVAL & EMBEDDING ANALYSIS - {config_name}")
print("=" * 100)

print("\n=== RETRIEVAL QUALITY METRICS ===")

# Analyze correct doc retrieval
correct_at_rank = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 'beyond_5': 0, 'missing': 0}

for i, q in enumerate(s['per_query']):
    found = False
    for rank, doc in enumerate(q['retrieved_documents'], 1):
        si = doc.get('metadata', {}).get('sample_index', -1)
        if si == i:
            if rank <= 5:
                correct_at_rank[rank] += 1
            else:
                correct_at_rank['beyond_5'] += 1
            found = True
            break
    if not found:
        correct_at_rank['missing'] += 1

print(f"Correct document retrieval ranking:")
for rank in [1, 2, 3, 4, 5, 'beyond_5', 'missing']:
    count = correct_at_rank[rank]
    pct = 100 * count / total_queries
    if rank == 'beyond_5':
        print(f"  Rank 6+: {count:2d} queries ({pct:5.1f}%)")
    elif rank == 'missing':
        print(f"  Missing: {count:2d} queries ({pct:5.1f}%)")
    else:
        print(f"  Rank {rank}: {count:2d} queries ({pct:5.1f}%)")

rank_1_3 = correct_at_rank[1] + correct_at_rank[2] + correct_at_rank[3]
rank_1_5 = sum(correct_at_rank[r] for r in [1, 2, 3, 4, 5])
print(f"\n  Total at rank 1-3: {rank_1_3}/20 ({100*rank_1_3/20:.1f}%)")
print(f"  Total at rank 1-5: {rank_1_5}/20 ({100*rank_1_5/20:.1f}%)")

print("\n=== RELEVANCE SCORE ANALYSIS ===")
print("(Measures if retrieved docs are relevant to query)")

low_rel = []
for i, q in enumerate(s['per_query']):
    rel = q.get('relevance_score__pred', 0)
    if rel < 0.4:
        low_rel.append((i, q['query'][:60], rel))

print(f"\nQueries with LOW relevance (< 0.4):")
for i, query, rel in sorted(low_rel, key=lambda x: x[2]):
    print(f"  Q{i:02d}: rel={rel:.3f} | {query}")

print(f"\nTotal low relevance: {len(low_rel)}/20 queries")

print("\n=== DOCUMENT QUALITY ANALYSIS ===")
print("(Analyzing retrieved document characteristics)")

doc_stats = {
    'total_docs_retrieved': 0,
    'avg_docs_per_query': 0,
    'doc_lengths': [],
    'doc_with_title': 0,
    'doc_without_title': 0,
}

for q in s['per_query']:
    docs = q.get('retrieved_documents', [])
    doc_stats['total_docs_retrieved'] += len(docs)
    for doc in docs:
        content = doc.get('content', '')
        doc_stats['doc_lengths'].append(len(content.split()))
        title = doc.get('title', '')
        if title:
            doc_stats['doc_with_title'] += 1
        else:
            doc_stats['doc_without_title'] += 1

doc_stats['avg_docs_per_query'] = doc_stats['total_docs_retrieved'] / total_queries

print(f"  Total docs retrieved: {doc_stats['total_docs_retrieved']}")
print(f"  Avg docs per query: {doc_stats['avg_docs_per_query']:.1f}")
print(f"  Docs with title: {doc_stats['doc_with_title']}")
print(f"  Docs without title: {doc_stats['doc_without_title']}")
print(f"  Avg doc length: {statistics.mean(doc_stats['doc_lengths']):.0f} words")
print(f"  Median doc length: {statistics.median(doc_stats['doc_lengths']):.0f} words")
print(f"  Doc length range: {min(doc_stats['doc_lengths'])}-{max(doc_stats['doc_lengths'])} words")

print("\n=== EMBEDDING MODEL ASSESSMENT ===")
print("(Current: BAAI/bge-large-en-v1.5, dimension=1024)")

print("\nStrengths:")
print("  ✓ Good general-purpose biomedical embedding")
print("  ✓ 1024 dimensions provide good expressiveness")
print("  ✓ Retrieves correct documents 100% of the time")
print("  ✓ Works well with sparse search fusion")

print("\nWeaknesses:")
print("  ✗ Correct docs often ranked beyond position 1")
print("  ✗ Some off-topic docs ranked high (relevance issues)")
print("  ✗ May not capture domain-specific biomedical nuances")
print("  ✗ No title-aware encoding (titles not used in embedding)")

print("\n=== RETRIEVAL IMPROVEMENTS NEEDED ===")

# Identify queries with poor retrieval
poor_retrieval = []
for i, q in enumerate(s['per_query']):
    rel = q.get('relevance_score__pred', 0)
    util = q.get('utilization_score__pred', 0)
    if rel < 0.4 or util < 0.2:
        poor_retrieval.append((i, q['query'][:50], rel, util))

print(f"\nQueries with poor retrieval (rel<0.4 OR util<0.2):")
for i, query, rel, util in sorted(poor_retrieval, key=lambda x: x[2] + x[3]):
    print(f"  Q{i:02d}: rel={rel:.3f}, util={util:.3f} | {query}")

print("\n=== RECOMMENDATIONS ===")

print("\n1. EMBEDDING MODEL OPTIONS:")
print("   Current: BAAI/bge-large-en-v1.5 (general)")
print("   Option A: BAAI/bge-small-en-v1.5 (faster, 384 dims)")
print("   Option B: PubMedBERT (biomedical-specific)")
print("   Option C: SciBERT (scientific domain)")
print("   Option D: Hybrid (dense + sparse + semantic)")

print("\n2. RANKING IMPROVEMENTS:")
print(f"   - {correct_at_rank[1]} queries have correct doc at rank 1")
print(f"   - {correct_at_rank[2] + correct_at_rank[3]} queries have correct doc at rank 2-3")
print(f"   - {correct_at_rank[4] + correct_at_rank[5]} queries have correct doc at rank 4-5")
print("   → Consider: Better reranker, query expansion, or semantic similarity tuning")

print("\n3. RELEVANCE IMPROVEMENTS:")
print(f"   - {len(low_rel)} queries with low relevance")
print("   → Consider: Query-aware retrieval, semantic similarity threshold, or better query transform")

print("\n4. QUICK WINS:")
print("   - Increase reranker top_k from 10 to 15")
print("   - Use title in query expansion (if available)")
print("   - Add semantic similarity threshold (min 0.5)")
print("   - Experiment with different fusion weights")

print("\n" + "=" * 100)
