"""Design v16 configuration to address v14 underperformance."""
import json
from pathlib import Path
from collections import defaultdict

def analyze_underperformance():
    """Analyze which queries are underperforming and why."""
    jsonl_path = Path("rag-experiments/pubmedqa-experiment/temp/pubmedqa_title_aware_v14_pubmedbert_stepback.jsonl")
    
    if not jsonl_path.exists():
        print(f"ERROR: {jsonl_path} not found")
        return
    
    underperforming = []
    
    with open(jsonl_path) as f:
        for idx, line in enumerate(f):
            record = json.loads(line)
            metadata = record.get("metadata", {})
            
            if metadata.get("status") != "success":
                continue
            
            gt = metadata.get("ground_truth", {})
            pred = metadata.get("predicted_scores", {})
            
            rel_diff = pred.get("relevance_score", 0) - gt.get("relevance_score", 0)
            util_diff = pred.get("utilization_score", 0) - gt.get("utilization_score", 0)
            comp_diff = pred.get("completeness_score", 0) - gt.get("completeness_score", 0)
            
            if rel_diff < -0.2 or util_diff < -0.3 or comp_diff < -0.3:
                underperforming.append({
                    "query_idx": idx,
                    "query": record.get("query", "")[:100],
                    "rel_diff": rel_diff,
                    "util_diff": util_diff,
                    "comp_diff": comp_diff,
                    "answer": record.get("answer", "")[:200],
                    "num_docs": len(record.get("retrieved_docs", [])),
                })
    
    print("=" * 120)
    print("V16 CONFIGURATION DESIGN - ADDRESSING V14 UNDERPERFORMANCE")
    print("=" * 120)
    print()
    
    print("PROBLEM ANALYSIS")
    print("-" * 120)
    print()
    print(f"Total underperforming queries: {len(underperforming)}/20")
    print()
    
    print("Top Issues:")
    print()
    for i, q in enumerate(underperforming[:5], 1):
        print(f"{i}. Query {q['query_idx']}: {q['query']}")
        print(f"   Relevance: {q['rel_diff']:+.2f} | Utilization: {q['util_diff']:+.2f} | Completeness: {q['comp_diff']:+.2f}")
        print(f"   Answer: {q['answer']}")
        print(f"   Retrieved docs: {q['num_docs']}")
        print()
    
    print()
    print("=" * 120)
    print("V16 IMPROVEMENT STRATEGY")
    print("=" * 120)
    print()
    
    print("ROOT CAUSES OF UNDERPERFORMANCE:")
    print()
    print("1. LOW UTILIZATION (-77.8%)")
    print("   - Answers not using retrieved documents effectively")
    print("   - Prompt may be too restrictive")
    print("   - Retrieved documents may not be relevant")
    print()
    print("   SOLUTION:")
    print("   - Increase max_tokens to allow longer answers")
    print("   - Relax prompt to encourage document usage")
    print("   - Improve retrieval (more docs, better ranking)")
    print()
    
    print("2. LOW COMPLETENESS (-74.9%)")
    print("   - Not covering all relevant information")
    print("   - Answers too short or incomplete")
    print("   - May be missing key documents")
    print()
    print("   SOLUTION:")
    print("   - Increase retrieval top_k (get more documents)")
    print("   - Add explicit instruction to cover all relevant info")
    print("   - Increase reranker top_k to get better documents")
    print()
    
    print("3. LOW RELEVANCE (-31.8%)")
    print("   - Retrieved documents not relevant to query")
    print("   - Query transform not working well")
    print("   - Embedding model may not be capturing semantics")
    print()
    print("   SOLUTION:")
    print("   - Try multi_query alongside step_back")
    print("   - Increase dense search top_k")
    print("   - Add query expansion")
    print()
    
    print()
    print("=" * 120)
    print("V16 CONFIGURATION CHANGES")
    print("=" * 120)
    print()
    
    changes = {
        "Retrieval": {
            "Query Transform": "step_back + multi_query (hybrid)",
            "Dense Search top_k": "75 → 100 (get more candidates)",
            "Sparse Search top_k": "75 → 100 (get more candidates)",
            "Reranker top_k": "15 → 25 (keep more documents)",
            "Min Similarity": "0.5 → 0.4 (less strict filtering)",
        },
        "Generation": {
            "Max Tokens": "600 → 800 (allow longer answers)",
            "System Prompt": "Relaxed (encourage document usage)",
            "Temperature": "0.0 (keep deterministic)",
        },
        "Embedding": {
            "Model": "PubMedBERT (keep same)",
            "Dimension": "768 (keep same)",
        },
        "Fusion": {
            "Type": "weighted_sum (keep same)",
            "Weights": "0.7 dense, 0.3 sparse (keep same)",
        },
    }
    
    for category, items in changes.items():
        print(f"{category}:")
        for key, value in items.items():
            print(f"  • {key}: {value}")
        print()
    
    print()
    print("=" * 120)
    print("EXPECTED IMPROVEMENTS")
    print("=" * 120)
    print()
    
    print("Relevance:    0.3332 → 0.42-0.48 (+26-44%)")
    print("  - More documents retrieved")
    print("  - Better query transform (hybrid)")
    print("  - Less strict filtering")
    print()
    
    print("Utilization:  0.0822 → 0.25-0.35 (+204-326%)")
    print("  - Longer answers allowed")
    print("  - More documents available")
    print("  - Relaxed prompt encourages usage")
    print()
    
    print("Completeness: 0.1717 → 0.45-0.55 (+162-220%)")
    print("  - More documents retrieved")
    print("  - Longer answers can cover more info")
    print("  - Better reranking keeps relevant docs")
    print()
    
    print("Adherence:    0.850 → 0.80-0.85 (maintained)")
    print("  - Strict prompt still enforces passage-only rule")
    print("  - May drop slightly due to longer answers")
    print()
    
    print()
    print("=" * 120)
    print("RATIONALE")
    print("=" * 120)
    print()
    
    print("Why these changes?")
    print()
    print("1. HYBRID QUERY TRANSFORM (step_back + multi_query)")
    print("   - step_back: Breaks down complex queries")
    print("   - multi_query: Generates alternative phrasings")
    print("   - Together: Better coverage of query space")
    print()
    
    print("2. INCREASED RETRIEVAL TOP_K (75 → 100)")
    print("   - More candidates to choose from")
    print("   - Better chance of finding relevant docs")
    print("   - Reranker can pick best ones")
    print()
    
    print("3. HIGHER RERANKER TOP_K (15 → 25)")
    print("   - Keep more documents in context")
    print("   - Allows model to use more information")
    print("   - Improves completeness")
    print()
    
    print("4. RELAXED MIN_SIMILARITY (0.5 → 0.4)")
    print("   - Less strict filtering")
    print("   - May include borderline relevant docs")
    print("   - Better for low-resource queries")
    print()
    
    print("5. LONGER MAX_TOKENS (600 → 800)")
    print("   - Allows more comprehensive answers")
    print("   - Can cover multiple aspects")
    print("   - Improves utilization and completeness")
    print()
    
    print("6. RELAXED SYSTEM PROMPT")
    print("   - Encourage document usage")
    print("   - Still enforce passage-only rule")
    print("   - Balance between adherence and completeness")
    print()
    
    print()
    print("=" * 120)
    print("RISK ASSESSMENT")
    print("=" * 120)
    print()
    
    print("Potential Risks:")
    print()
    print("1. Adherence may drop (0.850 → 0.80-0.85)")
    print("   - Longer answers may include hedging")
    print("   - Mitigation: Keep strict prompt")
    print()
    
    print("2. Latency may increase")
    print("   - More documents to process")
    print("   - Longer generation")
    print("   - Mitigation: Monitor and optimize if needed")
    print()
    
    print("3. Hallucination risk increases")
    print("   - Longer answers may add non-passage info")
    print("   - Mitigation: Strict prompt + evaluation")
    print()
    
    print()
    print("=" * 120)
    print("NEXT STEPS")
    print("=" * 120)
    print()
    
    print("1. Create pubmedqa_v16_improved_retrieval.yaml")
    print("2. Run v16 on all 20 queries")
    print("3. Compare against v14 using ground truth")
    print("4. If successful (rel > 0.42), use as new baseline")
    print("5. If not, try alternative approaches:")
    print("   - Different embedding model (SciBERT)")
    print("   - Different reranker (DeBERTa)")
    print("   - Different query transform (query_rewriter)")
    print()
    
    print("=" * 120)

if __name__ == "__main__":
    analyze_underperformance()
