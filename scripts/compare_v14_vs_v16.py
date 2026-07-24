"""Compare v14 vs v16 results against ground truth."""
import json
from pathlib import Path
from collections import defaultdict

def load_jsonl_scores(jsonl_path):
    """Load predicted and ground truth scores from JSONL."""
    metrics = defaultdict(list)
    query_details = []
    
    with open(jsonl_path) as f:
        for idx, line in enumerate(f):
            record = json.loads(line)
            metadata = record.get("metadata", {})
            
            if metadata.get("status") != "success":
                continue
            
            gt = metadata.get("ground_truth", {})
            pred = metadata.get("predicted_scores", {})
            
            for metric in ["relevance_score", "utilization_score", "completeness_score"]:
                if metric in gt and metric in pred:
                    metrics[f"{metric}_gt"].append(gt[metric])
                    metrics[f"{metric}_pred"].append(pred[metric])
            
            query_details.append({
                "query_idx": idx,
                "query": record.get("query", "")[:80],
                "gt_rel": gt.get("relevance_score"),
                "pred_rel": pred.get("relevance_score"),
                "gt_util": gt.get("utilization_score"),
                "pred_util": pred.get("utilization_score"),
                "gt_comp": gt.get("completeness_score"),
                "pred_comp": pred.get("completeness_score"),
            })
    
    return metrics, query_details

def calculate_stats(values):
    """Calculate mean, std, min, max."""
    if not values:
        return 0, 0, 0, 0
    mean = sum(values) / len(values)
    std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
    return mean, std, min(values), max(values)

def compare_configs():
    """Compare v14 vs v16."""
    
    v14_path = Path("rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl")
    v16_path = Path("rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v16_improved_retrieval.jsonl")
    
    print("=" * 120)
    print("V14 vs V16 COMPARISON")
    print("=" * 120)
    print()
    
    # Check if files exist
    if not v14_path.exists():
        print(f"ERROR: {v14_path} not found")
        return
    
    if not v16_path.exists():
        print(f"ERROR: {v16_path} not found")
        print()
        print("V16 has not been run yet. Please run v16 first:")
        print("  python3 scripts/run_v16_experiment.py")
        return
    
    print(f"✓ v14 found: {v14_path}")
    print(f"✓ v16 found: {v16_path}")
    print()
    
    # Load data
    v14_metrics, v14_details = load_jsonl_scores(v14_path)
    v16_metrics, v16_details = load_jsonl_scores(v16_path)
    
    print()
    print("=" * 120)
    print("AGGREGATE METRICS COMPARISON")
    print("=" * 120)
    print()
    
    print("Metric | v14 Mean | v16 Mean | Change | % Change | Status")
    print("-------|----------|----------|--------|----------|--------")
    
    for metric in ["relevance_score", "utilization_score", "completeness_score"]:
        v14_mean = sum(v14_metrics[f"{metric}_pred"]) / len(v14_metrics[f"{metric}_pred"])
        v16_mean = sum(v16_metrics[f"{metric}_pred"]) / len(v16_metrics[f"{metric}_pred"])
        
        change = v16_mean - v14_mean
        pct_change = (change / v14_mean * 100) if v14_mean != 0 else 0
        
        status = "✅" if change > 0 else "❌" if change < 0 else "="
        
        metric_short = metric.replace("_score", "").replace("_", " ").title()
        print(f"{metric_short:7} | {v14_mean:8.4f} | {v16_mean:8.4f} | {change:+7.4f} | {pct_change:+8.1f}% | {status}")
    
    print()
    print()
    print("=" * 120)
    print("GROUND TRUTH COMPARISON")
    print("=" * 120)
    print()
    
    print("Metric | Ground Truth | v14 Gap | v16 Gap | Improvement")
    print("-------|--------------|---------|---------|-------------")
    
    for metric in ["relevance_score", "utilization_score", "completeness_score"]:
        gt_mean = sum(v14_metrics[f"{metric}_gt"]) / len(v14_metrics[f"{metric}_gt"])
        v14_mean = sum(v14_metrics[f"{metric}_pred"]) / len(v14_metrics[f"{metric}_pred"])
        v16_mean = sum(v16_metrics[f"{metric}_pred"]) / len(v16_metrics[f"{metric}_pred"])
        
        v14_gap = v14_mean - gt_mean
        v16_gap = v16_mean - gt_mean
        improvement = v16_gap - v14_gap
        
        metric_short = metric.replace("_score", "").replace("_", " ").title()
        print(f"{metric_short:7} | {gt_mean:12.4f} | {v14_gap:+7.4f} | {v16_gap:+7.4f} | {improvement:+11.4f}")
    
    print()
    print()
    print("=" * 120)
    print("PER-QUERY COMPARISON (Top 10 Improvements)")
    print("=" * 120)
    print()
    
    # Calculate per-query improvements
    improvements = []
    for i in range(len(v14_details)):
        v14_d = v14_details[i]
        v16_d = v16_details[i]
        
        rel_imp = (v16_d["pred_rel"] - v14_d["pred_rel"]) if v16_d["pred_rel"] and v14_d["pred_rel"] else 0
        util_imp = (v16_d["pred_util"] - v14_d["pred_util"]) if v16_d["pred_util"] and v14_d["pred_util"] else 0
        comp_imp = (v16_d["pred_comp"] - v14_d["pred_comp"]) if v16_d["pred_comp"] and v14_d["pred_comp"] else 0
        
        total_imp = rel_imp + util_imp + comp_imp
        
        improvements.append({
            "query_idx": v14_d["query_idx"],
            "query": v14_d["query"],
            "rel_imp": rel_imp,
            "util_imp": util_imp,
            "comp_imp": comp_imp,
            "total_imp": total_imp,
        })
    
    # Sort by total improvement
    improvements.sort(key=lambda x: x["total_imp"], reverse=True)
    
    print("Query | Relevance | Utilization | Completeness | Total | Query")
    print("------|-----------|--------------|--------------|-------|------")
    
    for imp in improvements[:10]:
        print(f"Q{imp['query_idx']:02d}  | {imp['rel_imp']:+9.4f} | {imp['util_imp']:+12.4f} | {imp['comp_imp']:+12.4f} | {imp['total_imp']:+5.4f} | {imp['query']}")
    
    print()
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print()
    
    # Calculate overall stats
    v14_rel_mean = sum(v14_metrics["relevance_score_pred"]) / len(v14_metrics["relevance_score_pred"])
    v16_rel_mean = sum(v16_metrics["relevance_score_pred"]) / len(v16_metrics["relevance_score_pred"])
    
    v14_util_mean = sum(v14_metrics["utilization_score_pred"]) / len(v14_metrics["utilization_score_pred"])
    v16_util_mean = sum(v16_metrics["utilization_score_pred"]) / len(v16_metrics["utilization_score_pred"])
    
    v14_comp_mean = sum(v14_metrics["completeness_score_pred"]) / len(v14_metrics["completeness_score_pred"])
    v16_comp_mean = sum(v16_metrics["completeness_score_pred"]) / len(v16_metrics["completeness_score_pred"])
    
    print(f"Relevance:    {v14_rel_mean:.4f} → {v16_rel_mean:.4f} ({v16_rel_mean - v14_rel_mean:+.4f}, {(v16_rel_mean - v14_rel_mean) / v14_rel_mean * 100:+.1f}%)")
    print(f"Utilization:  {v14_util_mean:.4f} → {v16_util_mean:.4f} ({v16_util_mean - v14_util_mean:+.4f}, {(v16_util_mean - v14_util_mean) / v14_util_mean * 100:+.1f}%)")
    print(f"Completeness: {v14_comp_mean:.4f} → {v16_comp_mean:.4f} ({v16_comp_mean - v14_comp_mean:+.4f}, {(v16_comp_mean - v14_comp_mean) / v14_comp_mean * 100:+.1f}%)")
    print()
    
    # Determine status
    rel_imp = v16_rel_mean - v14_rel_mean
    util_imp = v16_util_mean - v14_util_mean
    comp_imp = v16_comp_mean - v14_comp_mean
    
    if rel_imp > 0.05 and util_imp > 0.05 and comp_imp > 0.05:
        print("✅ V16 SHOWS SIGNIFICANT IMPROVEMENT")
    elif rel_imp > 0 and util_imp > 0 and comp_imp > 0:
        print("✓ V16 SHOWS IMPROVEMENT")
    elif rel_imp > 0 or util_imp > 0 or comp_imp > 0:
        print("⚠️  V16 SHOWS MIXED RESULTS")
    else:
        print("❌ V16 SHOWS NO IMPROVEMENT")
    
    print()
    print("=" * 120)

if __name__ == "__main__":
    compare_configs()
