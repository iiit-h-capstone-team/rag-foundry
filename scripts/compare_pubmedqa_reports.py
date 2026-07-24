"""Compare pubmedqa_v11_query_transform vs pubmedqa_v12_improved_prompt reports."""
import json
import statistics
import sys
from pathlib import Path

def load_report(path):
    with open(path) as f:
        return json.load(f)

# Allow custom paths via command line
report1_path = sys.argv[1] if len(sys.argv) > 1 else 'rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v11_query_transform.json'
report2_path = sys.argv[2] if len(sys.argv) > 2 else 'rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v12_improved_prompt.json'

if not Path(report1_path).exists() or not Path(report2_path).exists():
    print(f"Error: One or both reports not found")
    print(f"  Report 1: {report1_path} {'✓' if Path(report1_path).exists() else '✗'}")
    print(f"  Report 2: {report2_path} {'✓' if Path(report2_path).exists() else '✗'}")
    sys.exit(1)

r1 = load_report(report1_path)
r2 = load_report(report2_path)

s1 = r1['sections'][0]
s2 = r2['sections'][0]

config1_name = s1.get('config_name', 'config1')
config2_name = s2.get('config_name', 'config2')

print("=" * 100)
print(f"COMPARISON: {config1_name} vs {config2_name}")
print("=" * 100)

# Aggregate metrics
print("\n=== AGGREGATE METRICS ===")
print(f"{'METRIC':<30} {'v11':>15} {'v12':>15} {'Δ':>12} {'% Change':>12}")
print("-" * 100)

metrics = ['relevance_score', 'utilization_score', 'completeness_score', 'adherence_score']

for metric in metrics:
    pred1_vals = [q.get(f'{metric}__pred', 0) for q in s1['per_query']]
    pred2_vals = [q.get(f'{metric}__pred', 0) for q in s2['per_query']]
    
    mean1 = statistics.mean(pred1_vals)
    mean2 = statistics.mean(pred2_vals)
    delta = mean2 - mean1
    pct_change = (delta / mean1 * 100) if mean1 != 0 else 0
    
    symbol = "↑" if delta > 0.01 else "↓" if delta < -0.01 else "→"
    print(f"  {metric:<28} {mean1:>15.3f} {mean2:>15.3f} {delta:>+12.3f} {pct_change:>+11.1f}% {symbol}")

# Per-query comparison
print("\n" + "=" * 100)
print("PER-QUERY COMPARISON (predicted scores)")
print("=" * 100)

pq1 = s1['per_query']
pq2 = s2['per_query']

# Match queries
q2_map = {q['query']: q for q in pq2}

n_better = {m: 0 for m in metrics}
n_worse = {m: 0 for m in metrics}
n_equal = {m: 0 for m in metrics}

print(f"\n{'Q':>3} {'Adherence':>15} {'Completeness':>15} {'Utilization':>15} {'Relevance':>15} Query")
print("-" * 100)

for i, q1 in enumerate(pq1):
    query = q1['query']
    q2 = q2_map.get(query)
    if not q2:
        print(f"  Q{i:02d}: Query not found in v12 report")
        continue
    
    # Calculate deltas for each metric
    diffs = {}
    for m in metrics:
        v1 = q1.get(f'{m}__pred', 0)
        v2 = q2.get(f'{m}__pred', 0)
        delta = v2 - v1
        diffs[m] = (v1, v2, delta)
        
        if delta > 0.01:
            n_better[m] += 1
        elif delta < -0.01:
            n_worse[m] += 1
        else:
            n_equal[m] += 1
    
    # Format output
    adh_v1, adh_v2, adh_d = diffs['adherence_score']
    com_v1, com_v2, com_d = diffs['completeness_score']
    uti_v1, uti_v2, uti_d = diffs['utilization_score']
    rel_v1, rel_v2, rel_d = diffs['relevance_score']
    
    adh_sym = "↑" if adh_d > 0.01 else "↓" if adh_d < -0.01 else "→"
    com_sym = "↑" if com_d > 0.01 else "↓" if com_d < -0.01 else "→"
    uti_sym = "↑" if uti_d > 0.01 else "↓" if uti_d < -0.01 else "→"
    rel_sym = "↑" if rel_d > 0.01 else "↓" if rel_d < -0.01 else "→"
    
    print(f"  Q{i:02d} {adh_v1:.2f}→{adh_v2:.2f}{adh_sym:>2} {com_v1:.2f}→{com_v2:.2f}{com_sym:>2} {uti_v1:.2f}→{uti_v2:.2f}{uti_sym:>2} {rel_v1:.2f}→{rel_v2:.2f}{rel_sym:>2} {query[:40]}")

print("\n" + "=" * 100)
print("WIN/LOSS SUMMARY (v11 vs v12)")
print("=" * 100)
for m in metrics:
    total = n_better[m] + n_worse[m] + n_equal[m]
    print(f"  {m:<30} Better={n_better[m]:>2}  Worse={n_worse[m]:>2}  Equal={n_equal[m]:>2}  (Total={total})")

# Detailed improvements
print("\n" + "=" * 100)
print("QUERIES WITH BIGGEST IMPROVEMENTS (v12 > v11)")
print("=" * 100)

improvements = []
for i, q1 in enumerate(pq1):
    query = q1['query']
    q2 = q2_map.get(query)
    if not q2:
        continue
    
    # Calculate overall improvement (sum of deltas)
    total_delta = 0
    for m in metrics:
        v1 = q1.get(f'{m}__pred', 0)
        v2 = q2.get(f'{m}__pred', 0)
        total_delta += (v2 - v1)
    
    improvements.append((i, query, total_delta, q1, q2))

improvements.sort(key=lambda x: x[2], reverse=True)

for i, query, total_delta, q1, q2 in improvements[:10]:
    if total_delta > 0.01:
        adh1 = q1.get('adherence_score__pred', 0)
        adh2 = q2.get('adherence_score__pred', 0)
        com1 = q1.get('completeness_score__pred', 0)
        com2 = q2.get('completeness_score__pred', 0)
        print(f"  Q{i:02d} Δ={total_delta:+.3f} | Adh: {adh1:.2f}→{adh2:.2f} | Com: {com1:.2f}→{com2:.2f}")
        print(f"       {query[:75]}")

print("\n" + "=" * 100)
print("QUERIES WITH BIGGEST REGRESSIONS (v12 < v11)")
print("=" * 100)

improvements.sort(key=lambda x: x[2])

for i, query, total_delta, q1, q2 in improvements[:10]:
    if total_delta < -0.01:
        adh1 = q1.get('adherence_score__pred', 0)
        adh2 = q2.get('adherence_score__pred', 0)
        com1 = q1.get('completeness_score__pred', 0)
        com2 = q2.get('completeness_score__pred', 0)
        print(f"  Q{i:02d} Δ={total_delta:+.3f} | Adh: {adh1:.2f}→{adh2:.2f} | Com: {com1:.2f}→{com2:.2f}")
        print(f"       {query[:75]}")

print("\n" + "=" * 100)
