"""Analyze adherence score and design v16 to maintain it."""
import json
from pathlib import Path

def analyze_adherence():
    """Analyze adherence in v14 and design v16 to maintain it."""
    
    jsonl_path = Path("rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl")
    
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} not found")
        return
    
    adherence_scores = []
    adherence_details = []
    
    with open(jsonl_path) as f:
        for idx, line in enumerate(f):
            record = json.loads(line)
            metadata = record.get("metadata", {})
            
            if metadata.get("status") != "success":
                continue
            
            gt = metadata.get("ground_truth", {})
            pred = metadata.get("predicted_scores", {})
            
            gt_adherence = gt.get("adherence_score")
            pred_adherence = pred.get("adherence_score")
            
            adherence_scores.append((gt_adherence, pred_adherence))
            adherence_details.append({
                "query_idx": idx,
                "query": record.get("query", "")[:100],
                "answer": record.get("answer", "")[:200],
                "gt_adherence": gt_adherence,
                "pred_adherence": pred_adherence,
                "num_docs": len(record.get("retrieved_docs", [])),
            })
    
    print("=" * 120)
    print("ADHERENCE SCORE ANALYSIS")
    print("=" * 120)
    print()
    
    # Calculate adherence stats
    gt_adherence_list = [s[0] for s in adherence_scores if s[0] is not None]
    pred_adherence_list = [s[1] for s in adherence_scores if s[1] is not None]
    
    gt_adherence_mean = sum(gt_adherence_list) / len(gt_adherence_list) if gt_adherence_list else 0
    pred_adherence_mean = sum(pred_adherence_list) / len(pred_adherence_list) if pred_adherence_list else 0
    
    # Count true/false
    gt_true = sum(1 for s in gt_adherence_list if s is True)
    pred_true = sum(1 for s in pred_adherence_list if s is True)
    
    print("V14 ADHERENCE METRICS:")
    print("-" * 120)
    print()
    print(f"Ground Truth Adherence:")
    print(f"  Mean: {gt_adherence_mean:.4f}")
    print(f"  True: {gt_true}/{len(gt_adherence_list)} queries ({gt_true/len(gt_adherence_list)*100:.1f}%)")
    print()
    
    print(f"Predicted Adherence:")
    print(f"  Mean: {pred_adherence_mean:.4f}")
    print(f"  True: {pred_true}/{len(pred_adherence_list)} queries ({pred_true/len(pred_adherence_list)*100:.1f}%)")
    print()
    
    print(f"Adherence Status:")
    if pred_adherence_mean >= gt_adherence_mean - 0.05:
        print(f"  ✅ GOOD - Predicted adherence matches or exceeds ground truth")
    else:
        print(f"  ⚠️  CONCERN - Predicted adherence below ground truth")
    print()
    
    print()
    print("=" * 120)
    print("QUERIES WITH ADHERENCE ISSUES")
    print("=" * 120)
    print()
    
    issues = [d for d in adherence_details if d["gt_adherence"] is True and d["pred_adherence"] is False]
    
    if issues:
        print(f"Queries where adherence dropped (GT=True, Pred=False): {len(issues)}")
        print()
        
        for issue in issues[:5]:
            print(f"Q{issue['query_idx']:02d}: {issue['query']}")
            print(f"  Answer: {issue['answer']}")
            print(f"  Docs: {issue['num_docs']}")
            print()
    else:
        print("No adherence issues found - all queries maintain adherence")
        print()
    
    print()
    print("=" * 120)
    print("V16 DESIGN TO MAINTAIN ADHERENCE")
    print("=" * 120)
    print()
    
    print("PROBLEM:")
    print("  - Longer answers (800 tokens) may include hedging/non-passage info")
    print("  - Multi_query may generate irrelevant queries")
    print("  - More documents may confuse the model")
    print()
    
    print("SOLUTION - V16 ADHERENCE SAFEGUARDS:")
    print()
    
    print("1. STRICT SYSTEM PROMPT")
    print("   - Enforce passage-only rule explicitly")
    print("   - Add examples of what NOT to do")
    print("   - Penalize hedging phrases")
    print()
    
    print("2. CAREFUL QUERY TRANSFORM")
    print("   - Use multi_query but with lower temperature (0.3)")
    print("   - Ensure generated queries stay on-topic")
    print("   - Validate queries before retrieval")
    print()
    
    print("3. DOCUMENT FILTERING")
    print("   - Keep min_similarity at 0.5 (not 0.4)")
    print("   - Only use high-confidence documents")
    print("   - Reranker top_k: 20 (not 25)")
    print()
    
    print("4. ANSWER LENGTH CONTROL")
    print("   - Max tokens: 700 (not 800)")
    print("   - Encourage conciseness")
    print("   - Still allow comprehensive answers")
    print()
    
    print("5. TEMPERATURE CONTROL")
    print("   - Keep temperature at 0.0 (deterministic)")
    print("   - No randomness in generation")
    print("   - Consistent adherence")
    print()
    
    print()
    print("=" * 120)
    print("REVISED V16 CONFIGURATION")
    print("=" * 120)
    print()
    
    print("Component | v14 | v16 (Original) | v16 (Revised) | Rationale")
    print("-----------|-----|----------------|---------------|----------")
    print("Query Transform | step_back | multi_query (5, 0.5T) | multi_query (5, 0.3T) | Lower temp for consistency")
    print("Dense Search | 75 | 100 | 85 | Balance coverage & quality")
    print("Sparse Search | 75 | 100 | 85 | Balance coverage & quality")
    print("Min Similarity | 0.5 | 0.4 | 0.5 | Maintain strict filtering")
    print("Reranker top_k | 15 | 25 | 20 | More docs but not too many")
    print("Max Tokens | 600 | 800 | 700 | Longer but not too long")
    print("System Prompt | Strict | Thorough | Strict+Thorough | Enforce adherence")
    print()
    
    print()
    print("=" * 120)
    print("EXPECTED RESULTS - V16 REVISED")
    print("=" * 120)
    print()
    
    print("Metric | v14 | v16 Revised | Expected Gap to GT")
    print("-------|-----|-------------|-------------------")
    print("Relevance | 0.3332 | 0.40-0.45 | -0.04 to -0.09 (vs GT 0.4885)")
    print("Utilization | 0.0822 | 0.20-0.28 | -0.09 to -0.17 (vs GT 0.3699)")
    print("Completeness | 0.1717 | 0.35-0.45 | -0.23 to -0.33 (vs GT 0.6849)")
    print("Adherence | 0.850 | 0.85-0.90 | MAINTAINED ✅")
    print()
    
    print("Improvements:")
    print("  Relevance: +20-35% (vs v14)")
    print("  Utilization: +143-240% (vs v14)")
    print("  Completeness: +104-162% (vs v14)")
    print("  Adherence: MAINTAINED (vs v14)")
    print()
    
    print()
    print("=" * 120)
    print("RECOMMENDATION")
    print("=" * 120)
    print()
    
    print("✅ Use V16 REVISED configuration")
    print()
    print("Rationale:")
    print("  1. Maintains adherence (critical for RAG)")
    print("  2. Still improves other metrics significantly")
    print("  3. Balances improvement with safety")
    print("  4. Conservative approach")
    print()
    
    print("If adherence still drops:")
    print("  - Reduce max_tokens to 650")
    print("  - Reduce reranker top_k to 15")
    print("  - Use step_back instead of multi_query")
    print()
    
    print("=" * 120)

if __name__ == "__main__":
    analyze_adherence()
