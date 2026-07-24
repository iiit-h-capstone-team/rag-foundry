"""Quick analysis of covidqa_title_aware_v1 report."""
import json

with open('reports/covidqa_title_aware_v1.json') as f:
    data = json.load(f)

section = data['sections'][0]

print('=== SUMMARY ===')
for m in section['summary']:
    print(f"  {m['metric']}: pred={m['mean_score']:.4f}  gt={m['mean_ground_truth']:.4f}  mae={m['mean_abs_error']:.4f}")

print('\n=== PER-QUERY BREAKDOWN ===')
for i, q in enumerate(section['per_query'][:20]):
    scores = q.get('predicted_scores', {})
    gt = q.get('ground_truth', {})
    rel_p = scores.get('relevance_score', '?')
    rel_gt = gt.get('relevance_score', '?')
    comp_p = scores.get('completeness_score', '?')
    comp_gt = gt.get('completeness_score', '?')

    samples = sorted(set(
        doc.get('metadata', {}).get('sample_index', -1)
        for doc in q.get('retrieved_documents', [])
    ))
    n_docs = len(q.get('retrieved_documents', []))
    query_short = q['query'][:80]
    print(f"  Q{i:02d}: rel={rel_p}/{rel_gt} comp={comp_p}/{comp_gt} docs={n_docs} samples={samples}")
    print(f"        {query_short}")

print('\n=== SAMPLE INDEX ANALYSIS ===')
total_docs = 0
same_sample = 0
for i, q in enumerate(section['per_query'][:20]):
    for doc in q.get('retrieved_documents', []):
        total_docs += 1
        si = doc.get('metadata', {}).get('sample_index', -1)
        if si == i:
            same_sample += 1

print(f"  Total retrieved docs: {total_docs}")
print(f"  Docs from correct sample (index==query_index): {same_sample} ({100*same_sample/max(total_docs,1):.1f}%)")
print(f"  Docs from other samples: {total_docs - same_sample}")
