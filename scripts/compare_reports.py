"""Compare covidqa_title_aware_v1 vs covidqa_high_recall_hybrid_v2 reports."""
import json

def load_report(path):
    with open(path) as f:
        return json.load(f)

r1 = load_report('reports/covidqa_title_aware_v1.json')
r2 = load_report('reports/covidqa_high_recall_hybrid_v2.json')

s1 = r1['sections'][0]
s2 = r2['sections'][0]

# Summary metrics
print("=" * 80)
print(f"{'METRIC':<25} {'title_aware_v1':>18} {'high_recall_v2':>18} {'delta':>10}")
print("=" * 80)

metrics1 = {m['metric']: m for m in s1['summary']}
metrics2 = {m['metric']: m for m in s2['summary']}

all_metrics = sorted(set(list(metrics1.keys()) + list(metrics2.keys())))
for metric in all_metrics:
    m1 = metrics1.get(metric, {})
    m2 = metrics2.get(metric, {})
    
    pred1 = m1.get('mean_score', float('nan'))
    pred2 = m2.get('mean_score', float('nan'))
    gt1 = m1.get('mean_ground_truth', float('nan'))
    gt2 = m2.get('mean_ground_truth', float('nan'))
    mae1 = m1.get('mean_abs_error', float('nan'))
    mae2 = m2.get('mean_abs_error', float('nan'))
    
    delta_pred = pred1 - pred2 if pred1 == pred1 and pred2 == pred2 else float('nan')
    
    print(f"\n  {metric}")
    print(f"    {'predicted':<17} {pred1:>18.4f} {pred2:>18.4f} {delta_pred:>+10.4f}")
    print(f"    {'ground_truth':<17} {gt1:>18.4f} {gt2:>18.4f}")
    print(f"    {'MAE':<17} {mae1:>18.4f} {mae2:>18.4f}")

# Per-query comparison
print("\n" + "=" * 80)
print("PER-QUERY COMPARISON (predicted scores)")
print("=" * 80)

pq1 = s1['per_query']
pq2 = s2['per_query']

# Match queries
q2_map = {q['query']: q for q in pq2}

n_better = {m: 0 for m in all_metrics}
n_worse = {m: 0 for m in all_metrics}
n_equal = {m: 0 for m in all_metrics}

for i, q1 in enumerate(pq1):
    query = q1['query']
    q2 = q2_map.get(query)
    if not q2:
        continue
    
    scores1 = q1.get('predicted_scores', q1.get('evaluation', {}))
    scores2 = q2.get('predicted_scores', q2.get('evaluation', {}))
    gt1 = q1.get('ground_truth', {})
    gt2 = q2.get('ground_truth', {})
    
    diffs = []
    for m in all_metrics:
        v1 = scores1.get(m)
        v2 = scores2.get(m)
        if v1 is not None and v2 is not None:
            d = v1 - v2
            diffs.append(f"{m[:4]}={v1:.2f}/{v2:.2f}({d:+.2f})")
            if d > 0.01:
                n_better[m] += 1
            elif d < -0.01:
                n_worse[m] += 1
            else:
                n_equal[m] += 1
    
    # Sample index retrieval check
    samples1 = sorted(set(
        doc.get('metadata', {}).get('sample_index', -1)
        for doc in q1.get('retrieved_documents', [])
    ))
    samples2 = sorted(set(
        doc.get('metadata', {}).get('sample_index', -1)
        for doc in q2.get('retrieved_documents', [])
    ))
    has_correct1 = i in samples1
    has_correct2 = i in samples2
    
    print(f"  Q{i:02d} [{'+' if has_correct1 else '-'}|{'+' if has_correct2 else '-'}]: {' | '.join(diffs)}")
    print(f"       {query[:75]}")

print("\n" + "=" * 80)
print("WIN/LOSS SUMMARY (title_aware_v1 vs high_recall_v2)")
print("=" * 80)
for m in all_metrics:
    print(f"  {m:<25} better={n_better[m]:>3}  worse={n_worse[m]:>3}  equal={n_equal[m]:>3}")

# Correct sample retrieval
print("\n" + "=" * 80)
print("CORRECT SAMPLE RETRIEVAL")
print("=" * 80)
for label, section in [("title_aware_v1", s1), ("high_recall_v2", s2)]:
    total = 0
    correct = 0
    for i, q in enumerate(section['per_query']):
        for doc in q.get('retrieved_documents', []):
            total += 1
            si = doc.get('metadata', {}).get('sample_index', -1)
            if si == i:
                correct += 1
    print(f"  {label}: {correct}/{total} docs from correct sample ({100*correct/max(total,1):.1f}%)")
