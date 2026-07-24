"""Analyze per-query weaknesses in pubmedqa_title_aware_v11_query_transform report."""
import json
import statistics
import sys
from pathlib import Path

# Default to pubmedqa v11, but allow override via command line
report_path = sys.argv[1] if len(sys.argv) > 1 else 'rag-experiments/pubmedqa-experiment/reports/pubmedqa_title_aware_v11_query_transform.json'

if not Path(report_path).exists():
    print(f"Error: Report not found at {report_path}")
    sys.exit(1)

with open(report_path) as f:
    data = json.load(f)

s = data['sections'][0]
config_name = s.get('config_name', 'unknown')

print("=" * 80)
print(f"ANALYSIS: {config_name}")
print("=" * 80)

print("\n=== QUERIES WITH WORST ADHERENCE (pred vs GT) ===")
for q in sorted(s['per_query'], key=lambda q: abs(q.get('adherence_score__pred',0) - q.get('adherence_score__gt',0)), reverse=True)[:5]:
    dev = abs(q['adherence_score__pred'] - q['adherence_score__gt'])
    print(f"  Δ={dev:.2f} | pred={q['adherence_score__pred']:.2f} gt={q['adherence_score__gt']:.2f} | {q['query'][:70]}")

print("\n=== QUERIES WITH WORST COMPLETENESS (pred vs GT) ===")
for q in sorted(s['per_query'], key=lambda q: abs(q.get('completeness_score__pred',0) - q.get('completeness_score__gt',0)), reverse=True)[:5]:
    dev = abs(q['completeness_score__pred'] - q['completeness_score__gt'])
    print(f"  Δ={dev:.2f} | pred={q['completeness_score__pred']:.2f} gt={q['completeness_score__gt']:.2f} | {q['query'][:70]}")

print("\n=== QUERIES WITH LOW UTILIZATION ===")
for q in sorted(s['per_query'], key=lambda q: q.get('utilization_score__pred', 0))[:5]:
    print(f"  util={q['utilization_score__pred']:.3f} gt={q['utilization_score__gt']:.3f} ndocs={len(q['retrieved_documents'])} | {q['query'][:60]}")

print("\n=== QUERIES WITH LOW RELEVANCE ===")
for q in sorted(s['per_query'], key=lambda q: q.get('relevance_score__pred', 0))[:5]:
    print(f"  rel={q['relevance_score__pred']:.3f} gt={q['relevance_score__gt']:.3f} | {q['query'][:60]}")

print("\n=== ANSWER LENGTH ANALYSIS ===")
lengths = []
verbose_count = 0
for q in s['per_query']:
    ans = q.get('answer', '')
    wc = len(ans.split())
    lengths.append(wc)
    adh_p = q.get('adherence_score__pred', 0)
    adh_gt = q.get('adherence_score__gt', 0)
    if wc > 150:
        verbose_count += 1
        print(f"  VERBOSE ({wc}w) adh={adh_p:.2f}/{adh_gt:.2f} | {q['query'][:55]}")

print(f"\n  Mean answer length: {statistics.mean(lengths):.0f} words")
print(f"  Median: {statistics.median(lengths):.0f}, Max: {max(lengths)}, Min: {min(lengths)}")
print(f"  Verbose answers (>150w): {verbose_count}")

print("\n=== RETRIEVAL: CORRECT DOC RANK ===")
missing_correct = 0
for i, q in enumerate(s['per_query']):
    correct_ranks = []
    for rank, doc in enumerate(q['retrieved_documents']):
        si = doc.get('metadata', {}).get('sample_index', -1)
        if si == i:
            correct_ranks.append(rank + 1)
    if correct_ranks:
        if correct_ranks[0] > 3:
            print(f"  Q{i:02d}: correct docs at ranks {correct_ranks} (LATE!) | {q['query'][:55]}")
    else:
        missing_correct += 1
        print(f"  Q{i:02d}: NO correct docs retrieved | {q['query'][:55]}")

print(f"\n  Missing correct docs: {missing_correct}/{len(s['per_query'])}")

print("\n=== AGGREGATE METRICS ===")
metrics = ['relevance_score', 'utilization_score', 'completeness_score', 'adherence_score']
for metric in metrics:
    pred_vals = [q.get(f'{metric}__pred', 0) for q in s['per_query']]
    gt_vals = [q.get(f'{metric}__gt', 0) for q in s['per_query']]
    dev_vals = [abs(p - g) for p, g in zip(pred_vals, gt_vals)]
    print(f"  {metric}:")
    print(f"    Pred: {statistics.mean(pred_vals):.3f} ± {statistics.stdev(pred_vals):.3f}")
    print(f"    GT:   {statistics.mean(gt_vals):.3f} ± {statistics.stdev(gt_vals):.3f}")
    print(f"    Δ:    {statistics.mean(dev_vals):.3f} (avg deviation)")

print("\n=== KEY IMPROVEMENTS NEEDED ===")
# Identify top issues
adherence_issues = sum(1 for q in s['per_query'] if abs(q.get('adherence_score__pred',0) - q.get('adherence_score__gt',0)) > 0.5)
completeness_issues = sum(1 for q in s['per_query'] if abs(q.get('completeness_score__pred',0) - q.get('completeness_score__gt',0)) > 0.3)
utilization_issues = sum(1 for q in s['per_query'] if q.get('utilization_score__pred', 0) < 0.3)
relevance_issues = sum(1 for q in s['per_query'] if q.get('relevance_score__pred', 0) < 0.4)

print(f"  • Adherence issues: {adherence_issues} queries")
print(f"  • Completeness issues: {completeness_issues} queries")
print(f"  • Utilization issues: {utilization_issues} queries")
print(f"  • Relevance issues: {relevance_issues} queries")
print(f"  • Verbose answers: {verbose_count} queries (>150 words)")
print(f"  • Missing correct docs: {missing_correct} queries")

print("\n" + "=" * 80)
