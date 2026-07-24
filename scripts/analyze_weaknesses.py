"""Analyze per-query weaknesses in title_aware_v1 to guide config improvements."""
import json

with open('reports/covidqa_title_aware_v1.json') as f:
    data = json.load(f)

s = data['sections'][0]
metrics = ['relevance_score', 'utilization_score', 'completeness_score', 'adherence_score']

print("=== QUERIES WITH WORST ADHERENCE (pred vs GT) ===")
for q in sorted(s['per_query'], key=lambda q: abs(q.get('adherence_score__pred',0) - q.get('adherence_score__gt',0)), reverse=True)[:5]:
    print(f"  pred={q['adherence_score__pred']:.2f} gt={q['adherence_score__gt']:.2f} | {q['query'][:70]}")

print("\n=== QUERIES WITH WORST COMPLETENESS (pred vs GT) ===")
for q in sorted(s['per_query'], key=lambda q: abs(q.get('completeness_score__pred',0) - q.get('completeness_score__gt',0)), reverse=True)[:5]:
    print(f"  pred={q['completeness_score__pred']:.2f} gt={q['completeness_score__gt']:.2f} | {q['query'][:70]}")

print("\n=== QUERIES WITH LOW UTILIZATION ===")
for q in sorted(s['per_query'], key=lambda q: q.get('utilization_score__pred', 0))[:5]:
    print(f"  util={q['utilization_score__pred']:.3f} gt={q['utilization_score__gt']:.3f} ndocs={len(q['retrieved_documents'])} | {q['query'][:60]}")

print("\n=== ANSWER LENGTH ANALYSIS ===")
lengths = []
for q in s['per_query']:
    ans = q.get('answer', '')
    wc = len(ans.split())
    lengths.append(wc)
    adh_p = q.get('adherence_score__pred', 0)
    adh_gt = q.get('adherence_score__gt', 0)
    if wc > 100:
        print(f"  VERBOSE ({wc}w) adh={adh_p:.2f}/{adh_gt:.2f} | {q['query'][:55]}")

import statistics
print(f"\n  Mean answer length: {statistics.mean(lengths):.0f} words")
print(f"  Median: {statistics.median(lengths):.0f}, Max: {max(lengths)}, Min: {min(lengths)}")

print("\n=== RETRIEVAL: CORRECT DOC RANK ===")
for i, q in enumerate(s['per_query']):
    correct_ranks = []
    for rank, doc in enumerate(q['retrieved_documents']):
        si = doc.get('metadata', {}).get('sample_index', -1)
        if si == i:
            correct_ranks.append(rank + 1)
    if correct_ranks:
        print(f"  Q{i:02d}: correct docs at ranks {correct_ranks} | {q['query'][:55]}")
    else:
        print(f"  Q{i:02d}: NO correct docs retrieved | {q['query'][:55]}")
