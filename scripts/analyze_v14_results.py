"""Analyze v14 results from JSONL file."""
import json
import sys
from pathlib import Path
from collections import defaultdict

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
print("V14 RESULTS ANALYSIS - PubMedBERT + Step-Back Query Transform")
print("=" * 100)

# Aggregate metrics
metrics = {
    'relevance': [],
    'utilization': [],
    'completeness': [],
    'adherence': []
}

problem_queries = {
    10: "Surgery/Radiotherapy timing",
    17: "TB data reliability",
    6: "Disability pension",
    3: "Elderly fluids"
}

print("\n=== AGGREGATE METRICS ===\n")

for result in results:
    gt = result['metadata']['ground_truth']
    metrics['relevance'].append(gt['relevance_score'])
    metrics['utilization'].append(gt['utilization_score'])
    metrics['completeness'].append(gt['completeness_score'])
    metrics['adherence'].append(1 if gt['adherence_score'] else 0)

for metric_name, values in metrics.items():
    mean_val = sum(values) / len(values)
    print(f"{metric_name.upper():15} | Mean: {mean_val:.4f} | Min: {min(values):.4f} | Max: {max(values):.4f}")

print("\n=== PROBLEM QUERY ANALYSIS ===\n")

for result in results:
    query_idx = result['metadata']['query_index']
    if query_idx in problem_queries:
        gt = result['metadata']['ground_truth']
        rel = gt['relevance_score']
        util = gt['utilization_score']
        adh = "✓" if gt['adherence_score'] else "✗"
        comp = gt['completeness_score']
        
        print(f"Q{query_idx:02d} ({problem_queries[query_idx]}):")
        print(f"  Relevance: {rel:.4f} | Utilization: {util:.4f} | Completeness: {comp:.4f} | Adherence: {adh}")
        print(f"  Answer: {result['answer'][:100]}...")
        print()

print("\n=== ADHERENCE ANALYSIS ===\n")

adherence_true = sum(1 for r in results if r['metadata']['ground_truth']['adherence_score'])
adherence_false = len(results) - adherence_true

print(f"Adherence TRUE:  {adherence_true}/20 ({100*adherence_true/20:.1f}%)")
print(f"Adherence FALSE: {adherence_false}/20 ({100*adherence_false/20:.1f}%)")

print("\nQueries with adherence=FALSE:")
for result in results:
    if not result['metadata']['ground_truth']['adherence_score']:
        query_idx = result['metadata']['query_index']
        query = result['query'][:60]
        print(f"  Q{query_idx:02d}: {query}")

print("\n=== UTILIZATION ANALYSIS ===\n")

low_util = []
for result in results:
    util = result['metadata']['ground_truth']['utilization_score']
    if util < 0.2:
        low_util.append((result['metadata']['query_index'], util, result['query'][:50]))

print(f"Queries with low utilization (< 0.2): {len(low_util)}/20")
for query_idx, util, query in sorted(low_util, key=lambda x: x[1]):
    print(f"  Q{query_idx:02d}: util={util:.4f} | {query}")

print("\n=== RELEVANCE ANALYSIS ===\n")

low_rel = []
for result in results:
    rel = result['metadata']['ground_truth']['relevance_score']
    if rel < 0.4:
        low_rel.append((result['metadata']['query_index'], rel, result['query'][:50]))

print(f"Queries with low relevance (< 0.4): {len(low_rel)}/20")
for query_idx, rel, query in sorted(low_rel, key=lambda x: x[1]):
    print(f"  Q{query_idx:02d}: rel={rel:.4f} | {query}")

print("\n=== RETRIEVAL QUALITY ===\n")

correct_at_rank = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 'beyond_5': 0, 'missing': 0}

for result in results:
    query_idx = result['metadata']['query_index']
    docs = result['retrieved_docs']
    
    found = False
    for rank, doc in enumerate(docs, 1):
        si = doc.get('metadata', {}).get('sample_index', -1)
        if si == query_idx:
            if rank <= 5:
                correct_at_rank[rank] += 1
            else:
                correct_at_rank['beyond_5'] += 1
            found = True
            break
    if not found:
        correct_at_rank['missing'] += 1

print("Correct document retrieval ranking:")
for rank in [1, 2, 3, 4, 5, 'beyond_5', 'missing']:
    count = correct_at_rank[rank]
    pct = 100 * count / 20
    if rank == 'beyond_5':
        print(f"  Rank 6+: {count:2d}/20 ({pct:5.1f}%)")
    elif rank == 'missing':
        print(f"  Missing: {count:2d}/20 ({pct:5.1f}%)")
    else:
        print(f"  Rank {rank}: {count:2d}/20 ({pct:5.1f}%)")

rank_1_3 = correct_at_rank[1] + correct_at_rank[2] + correct_at_rank[3]
rank_1_5 = sum(correct_at_rank[r] for r in [1, 2, 3, 4, 5])
print(f"\n  Total at rank 1-3: {rank_1_3}/20 ({100*rank_1_3/20:.1f}%)")
print(f"  Total at rank 1-5: {rank_1_5}/20 ({100*rank_1_5/20:.1f}%)")

print("\n=== LATENCY ANALYSIS ===\n")

retrieval_times = []
generation_times = []
total_times = []

for result in results:
    lat = result['metadata']['latencies']
    retrieval_times.append(lat['retrieval_ms'])
    generation_times.append(lat['generation_ms'])
    total_times.append(lat['total_ms'])

print(f"Retrieval latency:  {sum(retrieval_times)/len(retrieval_times):.0f}ms (avg)")
print(f"Generation latency: {sum(generation_times)/len(generation_times):.0f}ms (avg)")
print(f"Total latency:      {sum(total_times)/len(total_times):.0f}ms (avg)")

print("\n=== KEY FINDINGS ===\n")

# Compare with v13 expected
v13_metrics = {
    'relevance': 0.508,
    'utilization': 0.324,
    'completeness': 0.632,
    'adherence': 0.150
}

v14_metrics = {
    'relevance': sum(metrics['relevance']) / len(metrics['relevance']),
    'utilization': sum(metrics['utilization']) / len(metrics['utilization']),
    'completeness': sum(metrics['completeness']) / len(metrics['completeness']),
    'adherence': sum(metrics['adherence']) / len(metrics['adherence'])
}

print("v13 vs v14 Comparison:")
print()
for metric in ['relevance', 'utilization', 'completeness', 'adherence']:
    v13 = v13_metrics[metric]
    v14 = v14_metrics[metric]
    change = v14 - v13
    pct_change = 100 * change / v13 if v13 > 0 else 0
    
    status = "✅" if change > 0 else "❌" if change < 0 else "→"
    print(f"{metric.upper():15} | v13: {v13:.4f} → v14: {v14:.4f} | Change: {change:+.4f} ({pct_change:+.1f}%) {status}")

print("\n" + "=" * 100)
