"""Analyze ground truth vs predicted scores across all v14 queries."""
import json
from pathlib import Path
from collections import defaultdict

def analyze_v14_scores():
    jsonl_path = Path("rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl")
    
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} not found")
        return
    
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
            query = record.get("query", "")
            
            for metric in ["relevance_score", "utilization_score", "completeness_score", "adherence_score"]:
                if metric in gt and metric in pred:
                    metrics[f"{metric}_gt"].append(gt[metric])
                    metrics[f"{metric}_pred"].append(pred[metric])
            
            query_details.append({
                "query_idx": idx,
                "query": query[:80] + "..." if len(query) > 80 else query,
                "gt_relevance": gt.get("relevance_score"),
                "pred_relevance": pred.get("relevance_score"),
                "gt_utilization": gt.get("utilization_score"),
                "pred_utilization": pred.get("utilization_score"),
                "gt_completeness": gt.get("completeness_score"),
                "pred_completeness": pred.get("completeness_score"),
            })
    
    print("=" * 120)
    print("V14 GROUND TRUTH vs PREDICTED SCORES ANALYSIS")
    print("=" * 120)
    print()
    
    print("AGGREGATE METRICS")
    print("-" * 120)
    print()
    
    for metric in ["relevance_score", "utilization_score", "completeness_score"]:
        gt_vals = metrics[f"{metric}_gt"]
        pred_vals = metrics[f"{metric}_pred"]
        
        if not gt_vals:
            continue
        
        gt_mean = sum(gt_vals) / len(gt_vals)
        pred_mean = sum(pred_vals) / len(pred_vals)
        diff = pred_mean - gt_mean
        diff_pct = (diff / gt_mean * 100) if gt_mean != 0 else 0
        
        print(f"{metric}:")
        print(f"  Ground Truth Mean: {gt_mean:.4f}")
        print(f"  Predicted Mean:   {pred_mean:.4f}")
        print(f"  Difference:       {diff:+.4f} ({diff_pct:+.1f}%)")
        
        if diff < -0.1:
            print(f"  ⚠️  UNDERPERFORMING - Answers worse than expected")
        elif diff > 0.1:
            print(f"  ✅ OVERPERFORMING - Answers better than expected")
        else:
            print(f"  ✓ MATCHING - Answers meet expectations")
        print()
    
    print()
    print("PER-QUERY COMPARISON")
    print("-" * 120)
    print()
    
    print("Query | GT Rel | Pred Rel | Diff  | GT Util | Pred Util | Diff  | GT Comp | Pred Comp | Diff")
    print("------|--------|----------|-------|---------|-----------|-------|---------|-----------|-------")
    
    for detail in query_details:
        gt_rel = detail["gt_relevance"]
        pred_rel = detail["pred_relevance"]
        diff_rel = pred_rel - gt_rel if pred_rel is not None and gt_rel is not None else None
        
        gt_util = detail["gt_utilization"]
        pred_util = detail["pred_utilization"]
        diff_util = pred_util - gt_util if pred_util is not None and gt_util is not None else None
        
        gt_comp = detail["gt_completeness"]
        pred_comp = detail["pred_completeness"]
        diff_comp = pred_comp - gt_comp if pred_comp is not None and gt_comp is not None else None
        
        rel_str = f"{pred_rel:.2f}" if pred_rel is not None else "N/A"
        util_str = f"{pred_util:.2f}" if pred_util is not None else "N/A"
        comp_str = f"{pred_comp:.2f}" if pred_comp is not None else "N/A"
        
        diff_rel_str = f"{diff_rel:+.2f}" if diff_rel is not None else "N/A"
        diff_util_str = f"{diff_util:+.2f}" if diff_util is not None else "N/A"
        diff_comp_str = f"{diff_comp:+.2f}" if diff_comp is not None else "N/A"
        
        print(f"Q{detail['query_idx']:02d}  | {gt_rel:.2f}   | {rel_str:8} | {diff_rel_str:5} | {gt_util:.2f}    | {util_str:9} | {diff_util_str:5} | {gt_comp:.2f}    | {comp_str:9} | {diff_comp_str:5}")
    
    print()
    print("=" * 120)
    print("INTERPRETATION")
    print("=" * 120)
    print()
    print("Ground Truth = PubMedQA dataset labels (expected/correct scores)")
    print("Predicted = TRACe evaluation of actual answers")
    print()
    print("Positive Difference (+) = Answers BETTER than expected (overperforming)")
    print("Negative Difference (-) = Answers WORSE than expected (underperforming)")
    print("Near Zero (±0.05) = Answers match expectations (as expected)")
    print()
    
    print("KEY FINDINGS:")
    print("-" * 120)
    
    rel_diffs = [metrics[f"relevance_score_pred"][i] - metrics[f"relevance_score_gt"][i] 
                 for i in range(len(metrics[f"relevance_score_gt"]))]
    util_diffs = [metrics[f"utilization_score_pred"][i] - metrics[f"utilization_score_gt"][i] 
                  for i in range(len(metrics[f"utilization_score_gt"]))]
    comp_diffs = [metrics[f"completeness_score_pred"][i] - metrics[f"completeness_score_gt"][i] 
                  for i in range(len(metrics[f"completeness_score_gt"]))]
    
    underperforming_rel = sum(1 for d in rel_diffs if d < -0.1)
    overperforming_rel = sum(1 for d in rel_diffs if d > 0.1)
    
    underperforming_util = sum(1 for d in util_diffs if d < -0.1)
    overperforming_util = sum(1 for d in util_diffs if d > 0.1)
    
    underperforming_comp = sum(1 for d in comp_diffs if d < -0.1)
    overperforming_comp = sum(1 for d in comp_diffs if d > 0.1)
    
    print()
    print(f"Relevance:")
    print(f"  Underperforming (pred < gt - 0.1): {underperforming_rel}/20 queries")
    print(f"  Overperforming (pred > gt + 0.1):  {overperforming_rel}/20 queries")
    print()
    
    print(f"Utilization:")
    print(f"  Underperforming (pred < gt - 0.1): {underperforming_util}/20 queries")
    print(f"  Overperforming (pred > gt + 0.1):  {overperforming_util}/20 queries")
    print()
    
    print(f"Completeness:")
    print(f"  Underperforming (pred < gt - 0.1): {underperforming_comp}/20 queries")
    print(f"  Overperforming (pred > gt + 0.1):  {overperforming_comp}/20 queries")
    print()
    
    print("=" * 120)
    print("CONCLUSION")
    print("=" * 120)
    print()
    
    avg_rel_diff = sum(rel_diffs) / len(rel_diffs)
    avg_util_diff = sum(util_diffs) / len(util_diffs)
    avg_comp_diff = sum(comp_diffs) / len(comp_diffs)
    
    if avg_rel_diff < -0.15 or avg_util_diff < -0.15 or avg_comp_diff < -0.15:
        print("⚠️  V14 IS UNDERPERFORMING")
        print()
        print("The RAG system is generating answers that are WORSE than the expected ground truth.")
        print("This suggests the configuration needs improvement.")
        print()
        print(f"  Relevance underperformance:   {avg_rel_diff:+.4f}")
        print(f"  Utilization underperformance: {avg_util_diff:+.4f}")
        print(f"  Completeness underperformance: {avg_comp_diff:+.4f}")
        print()
    elif avg_rel_diff > 0.1 or avg_util_diff > 0.1 or avg_comp_diff > 0.1:
        print("✅ V14 IS OVERPERFORMING")
        print()
        print("The RAG system is generating answers that are BETTER than the expected ground truth.")
        print("This is excellent - the system exceeds expectations.")
        print()
        print(f"  Relevance overperformance:   {avg_rel_diff:+.4f}")
        print(f"  Utilization overperformance: {avg_util_diff:+.4f}")
        print(f"  Completeness overperformance: {avg_comp_diff:+.4f}")
        print()
    else:
        print("✓ V14 IS MEETING EXPECTATIONS")
        print()
        print("The RAG system is generating answers that match the expected ground truth.")
        print("Performance is as expected.")
        print()
        print(f"  Relevance difference:   {avg_rel_diff:+.4f}")
        print(f"  Utilization difference: {avg_util_diff:+.4f}")
        print(f"  Completeness difference: {avg_comp_diff:+.4f}")
        print()
    
    print("=" * 120)

if __name__ == "__main__":
    analyze_v14_scores()
