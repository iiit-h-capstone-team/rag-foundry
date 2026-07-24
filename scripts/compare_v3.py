"""Compare v3, v4, v5_medcpt, v5_pubmedbert, v6_qwen32b, v7_contextual, v8_best_blend reports side-by-side."""

import json, sys

REPORTS = [
    ("v3", "reports/covidqa_title_aware_v3.json"),
    ("v4", "reports/covidqa_title_aware_v4.json"),
    ("v5_medcpt", "reports/covidqa_title_aware_v5_medcpt.json"),
    ("v5_pubmed", "reports/covidqa_title_aware_v5_pubmedbert.json"),
    ("v6_qwen", "reports/covidqa_title_aware_v6_qwen32b.json"),
    ("v7_ctx", "reports/covidqa_title_aware_v7_contextual.json"),
    ("v8_blend", "reports/covidqa_title_aware_v8_best_blend.json"),
    ("v9_bio", "reports/covidqa_title_aware_v9_biomedical.json"),
    ("v10_8b", "reports/covidqa_title_aware_v10_8b_compact.json"),
    ("v11_qt", "reports/covidqa_title_aware_v11_query_transform.json"),
    ("v12_opt", "reports/covidqa_title_aware_v12_optimized.json"),
    ("v13_tuned", "reports/covidqa_title_aware_v13_tuned.json"),
]

METRICS = ["relevance_score", "utilization_score", "completeness_score", "adherence_score"]
METRIC_LABELS = ["relevance", "utilization", "completeness", "adherence"]

def load_report(path):
    with open(path) as f:
        return json.load(f)

def get_summary(report):
    """Extract mean scores and MAE from the first section's summary."""
    section = report["sections"][0]
    summary = {}
    for row in section["summary"]:
        metric = row.get("metric", "")
        mean = row.get("mean_score", row.get("mean", None))
        mae = row.get("mean_abs_error", None)
        if mae is None and "deviation" in row:
            mae = abs(row["deviation"])
        summary[metric] = {"mean": mean, "mae": mae}
    return summary

def get_per_query(report):
    """Extract per-query scores."""
    section = report["sections"][0]
    queries = []
    for q in section["per_query"]:
        entry = {"query": q.get("query", "")}
        for m in METRICS:
            entry[f"{m}_pred"] = q.get(f"{m}__pred", None)
            entry[f"{m}_gt"] = q.get(f"{m}__gt", None)
        queries.append(entry)
    return queries

# ── Load ──
data = {}
for label, path in REPORTS:
    try:
        data[label] = load_report(path)
    except FileNotFoundError:
        print(f"WARNING: {path} not found, skipping {label}")

# ── Summary table ──
print("=" * 80)
print("SUMMARY COMPARISON")
print("=" * 80)
header = f"{'Metric':<16}"
for label in data:
    header += f"  {label:>8} mean  {label:>8} MAE"
print(header)
print("-" * len(header))

summaries = {label: get_summary(r) for label, r in data.items()}

for m, ml in zip(METRICS, METRIC_LABELS):
    row = f"{ml:<16}"
    for label in data:
        s = summaries[label].get(m, {})
        mean = s.get("mean")
        mae = s.get("mae")
        row += f"  {mean:>12.4f}  {mae:>10.4f}" if mean is not None else "           N/A           N/A"
    print(row)

# ── Delta tables ──
def print_delta(label_a, label_b):
    if label_a not in data or label_b not in data:
        return
    print(f"\n{'=' * 80}")
    print(f"DELTA: {label_b} vs {label_a}")
    print("=" * 80)
    print(f"{'Metric':<16}  {'Δ mean':>10}  {'Δ MAE':>10}  {'Verdict':>10}")
    print("-" * 60)
    for m, ml in zip(METRICS, METRIC_LABELS):
        sa = summaries[label_a].get(m, {})
        sb = summaries[label_b].get(m, {})
        dm = (sb.get("mean", 0) or 0) - (sa.get("mean", 0) or 0)
        de = (sb.get("mae", 0) or 0) - (sa.get("mae", 0) or 0)
        verdict = "✓ better" if dm > 0.005 else ("✗ worse" if dm < -0.005 else "~ same")
        print(f"{ml:<16}  {dm:>+10.4f}  {de:>+10.4f}  {verdict:>10}")

# All deltas vs v3 (baseline)
print_delta("v3", "v4")
print_delta("v3", "v5_medcpt")
print_delta("v3", "v5_pubmed")
print_delta("v3", "v6_qwen")
print_delta("v3", "v7_ctx")
print_delta("v3", "v8_blend")
print_delta("v3", "v9_bio")
print_delta("v3", "v10_8b")
print_delta("v3", "v11_qt")
print_delta("v3", "v12_opt")
print_delta("v3", "v13_tuned")

# Also compare new ones against best previous (v5_medcpt)
print_delta("v5_medcpt", "v6_qwen")
print_delta("v5_medcpt", "v7_ctx")
print_delta("v5_medcpt", "v8_blend")
print_delta("v5_medcpt", "v9_bio")
print_delta("v5_medcpt", "v10_8b")
print_delta("v5_medcpt", "v11_qt")
print_delta("v5_medcpt", "v12_opt")
print_delta("v5_medcpt", "v13_tuned")

# Compare v8, v9, v10, v11, v12, v13 against v7 (their predecessor)
print_delta("v7_ctx", "v8_blend")
print_delta("v8_blend", "v9_bio")
print_delta("v9_bio", "v10_8b")
print_delta("v8_blend", "v11_qt")
print_delta("v11_qt", "v12_opt")
print_delta("v11_qt", "v13_tuned")

# ── Per-query deep dive function ──
def print_per_query_movers(base_label, target_label):
    if base_label not in data or target_label not in data:
        return
    pq_base = get_per_query(data[base_label])
    pq_target = get_per_query(data[target_label])
    n = min(len(pq_base), len(pq_target))

    print("\n" + "=" * 80)
    print(f"PER-QUERY: Biggest changes {base_label} → {target_label}")
    print("=" * 80)

    for m, ml in zip(METRICS, METRIC_LABELS):
        deltas = []
        for i in range(n):
            pb = pq_base[i].get(f"{m}_pred")
            pt = pq_target[i].get(f"{m}_pred")
            if pb is not None and pt is not None:
                deltas.append((i, pt - pb, pb, pt, pq_target[i]["query"][:80]))
        deltas.sort(key=lambda x: abs(x[1]), reverse=True)

        print(f"\n  {ml.upper()} — top 5 movers:")
        for idx, delta, old, new, q in deltas[:5]:
            direction = "↑" if delta > 0 else "↓"
            print(f"    Q{idx:>2}: {old:.3f} → {new:.3f} ({direction}{abs(delta):.3f})  {q}")

print_per_query_movers("v3", "v5_medcpt")
print_per_query_movers("v3", "v5_pubmed")
print_per_query_movers("v3", "v6_qwen")
print_per_query_movers("v3", "v7_ctx")
print_per_query_movers("v3", "v8_blend")
print_per_query_movers("v3", "v9_bio")
print_per_query_movers("v3", "v10_8b")
print_per_query_movers("v3", "v11_qt")
print_per_query_movers("v3", "v12_opt")
print_per_query_movers("v3", "v13_tuned")
print_per_query_movers("v5_medcpt", "v6_qwen")
print_per_query_movers("v5_medcpt", "v7_ctx")
print_per_query_movers("v5_medcpt", "v8_blend")
print_per_query_movers("v5_medcpt", "v9_bio")
print_per_query_movers("v5_medcpt", "v10_8b")
print_per_query_movers("v5_medcpt", "v11_qt")
print_per_query_movers("v5_medcpt", "v12_opt")
print_per_query_movers("v5_medcpt", "v13_tuned")
print_per_query_movers("v7_ctx", "v8_blend")
print_per_query_movers("v8_blend", "v9_bio")
print_per_query_movers("v9_bio", "v10_8b")
print_per_query_movers("v8_blend", "v11_qt")
print_per_query_movers("v11_qt", "v12_opt")
print_per_query_movers("v11_qt", "v13_tuned")

print()
