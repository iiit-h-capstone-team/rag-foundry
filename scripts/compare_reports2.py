"""Compare reports — detect score field format first."""
import json

def load_report(path):
    with open(path) as f:
        return json.load(f)

r1 = load_report('reports/covidqa_title_aware_v1.json')
r2 = load_report('reports/covidqa_high_recall_hybrid_v2.json')

s1 = r1['sections'][0]
s2 = r2['sections'][0]

# Detect score fields
q1_sample = s1['per_query'][0]
q2_sample = s2['per_query'][0]
print("=== REPORT FIELD STRUCTURE ===")
print(f"  v1 per_query keys: {[k for k in q1_sample.keys() if k not in ('query','retrieved_documents','answer')]}")
print(f"  v2 per_query keys: {[k for k in q2_sample.keys() if k not in ('query','retrieved_documents','answer')]}")

# Check nested structures
for key in q1_sample:
    if key not in ('query', 'retrieved_documents', 'answer'):
        val = q1_sample[key]
        if isinstance(val, dict):
            print(f"  v1 {key}: {list(val.keys())[:8]}")

for key in q2_sample:
    if key not in ('query', 'retrieved_documents', 'answer'):
        val = q2_sample[key]
        if isinstance(val, dict):
            print(f"  v2 {key}: {list(val.keys())[:8]}")

def get_scores(q):
    """Extract predicted scores from per-query entry (handles __pred suffix)."""
    result = {}
    for k, v in q.items():
        if k.endswith('__pred'):
            metric = k.replace('__pred', '')
            result[metric] = v
    return result

def get_gt(q):
    """Extract ground truth scores (handles __gt suffix)."""
    result = {}
    for k, v in q.items():
        if k.endswith('__gt'):
            metric = k.replace('__gt', '')
            result[metric] = v
    return result

print(f"\n  v1 Q0 scores: {get_scores(q1_sample)}")
print(f"  v1 Q0 gt: {get_gt(q1_sample)}")
print(f"  v2 Q0 scores: {get_scores(q2_sample)}")
print(f"  v2 Q0 gt: {get_gt(q2_sample)}")

# Now do the full comparison
metrics = ['relevance_score', 'utilization_score', 'completeness_score', 'adherence_score']

print("\n" + "=" * 90)
print(f"{'SUMMARY METRICS':<25} {'title_aware_v1':>18} {'high_recall_v2':>18} {'delta':>10}")
print("=" * 90)

metrics1 = {m['metric']: m for m in s1['summary']}
metrics2 = {m['metric']: m for m in s2['summary']}

for m in metrics:
    m1 = metrics1.get(m, {})
    m2 = metrics2.get(m, {})
    p1 = m1.get('mean_score', 0)
    p2 = m2.get('mean_score', 0)
    g1 = m1.get('mean_ground_truth', 0)
    g2 = m2.get('mean_ground_truth', 0)
    mae1 = m1.get('mean_abs_error', 0)
    mae2 = m2.get('mean_abs_error', 0)
    dp = p1 - p2
    print(f"  {m}")
    print(f"    {'predicted':<17} {p1:>18.4f} {p2:>18.4f} {dp:>+10.4f} {'<< BETTER' if dp > 0.02 else '<< WORSE' if dp < -0.02 else ''}")
    print(f"    {'ground_truth':<17} {g1:>18.4f} {g2:>18.4f}")
    print(f"    {'MAE':<17} {mae1:>18.4f} {mae2:>18.4f} {mae1-mae2:>+10.4f} {'<< BETTER' if mae1 < mae2 - 0.02 else '<< WORSE' if mae1 > mae2 + 0.02 else ''}")

# Correct sample retrieval
print("\n" + "=" * 90)
print("RETRIEVAL QUALITY")
print("=" * 90)

for label, section in [("title_aware_v1", s1), ("high_recall_v2", s2)]:
    total_docs = 0
    correct_docs = 0
    queries_with_correct = 0
    for i, q in enumerate(section['per_query']):
        has_correct = False
        for doc in q.get('retrieved_documents', []):
            total_docs += 1
            si = doc.get('metadata', {}).get('sample_index', -1)
            if si == i:
                correct_docs += 1
                has_correct = True
        if has_correct:
            queries_with_correct += 1
    n_queries = len(section['per_query'])
    print(f"  {label}:")
    print(f"    Queries with >=1 correct doc: {queries_with_correct}/{n_queries} ({100*queries_with_correct/n_queries:.0f}%)")
    print(f"    Correct docs total: {correct_docs}/{total_docs} ({100*correct_docs/max(total_docs,1):.1f}%)")
    print(f"    Avg docs/query: {total_docs/max(n_queries,1):.1f}")

# Per-query detail
print("\n" + "=" * 90)
print("PER-QUERY DETAIL")
print("=" * 90)

q2_map = {q['query']: q for q in s2['per_query']}

print(f"  {'Q#':<4} {'correct[v1|v2]':>14} {'rel_v1':>8} {'rel_v2':>8} {'comp_v1':>8} {'comp_v2':>8} {'adh_v1':>8} {'adh_v2':>8}")
print(f"  {'':4} {'':>14} {'gt':>8} {'gt':>8} {'gt':>8} {'gt':>8} {'gt':>8} {'gt':>8}")
print("-" * 90)

for i, q1 in enumerate(s1['per_query']):
    q2 = q2_map.get(q1['query'])
    if not q2:
        continue
    
    sc1 = get_scores(q1)
    sc2 = get_scores(q2)
    gt1 = get_gt(q1)
    gt2 = get_gt(q2)
    
    # Correct sample check
    s1_correct = any(doc.get('metadata',{}).get('sample_index',-1) == i for doc in q1.get('retrieved_documents',[]))
    s2_correct = any(doc.get('metadata',{}).get('sample_index',-1) == i for doc in q2.get('retrieved_documents',[]))
    
    def fmt(v):
        if v is None: return "   -   "
        if isinstance(v, bool): return f"{'  True ' if v else ' False '}"
        return f"{v:>7.3f}"
    
    tag = f"[{'+' if s1_correct else '-'}|{'+' if s2_correct else '-'}]"
    print(f"  Q{i:02d} {tag:>14} {fmt(sc1.get('relevance_score'))} {fmt(sc2.get('relevance_score'))} {fmt(sc1.get('completeness_score'))} {fmt(sc2.get('completeness_score'))} {fmt(sc1.get('adherence_score'))} {fmt(sc2.get('adherence_score'))}")
    print(f"  {'':4} {'':>14} {fmt(gt1.get('relevance_score'))} {fmt(gt2.get('relevance_score'))} {fmt(gt1.get('completeness_score'))} {fmt(gt2.get('completeness_score'))} {fmt(gt1.get('adherence_score'))} {fmt(gt2.get('adherence_score'))}")
    print(f"       {q1['query'][:70]}")
