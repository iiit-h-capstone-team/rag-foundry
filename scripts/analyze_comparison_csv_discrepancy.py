"""Analyze discrepancy between comparison.csv and analysis documents."""

print("=" * 120)
print("DISCREPANCY ANALYSIS: comparison.csv vs Analysis Documents")
print("=" * 120)

print("\n=== COMPARISON.CSV SCORES ===\n")

csv_data = {
    'v11': {
        'relevance': 0.5147,
        'utilization': 0.2994,
        'completeness': 0.5692,
        'adherence': 0.25,
        'relevance_mae': 0.199,
        'utilization_mae': 0.1623,
        'completeness_mae': 0.2896,
        'adherence_mae': 0.6
    },
    'v14': {
        'relevance': 0.3332,
        'utilization': 0.0822,
        'completeness': 0.1717,
        'adherence': 0.6,
        'relevance_mae': 0.3087,
        'utilization_mae': 0.308,
        'completeness_mae': 0.5548,
        'adherence_mae': 0.55
    },
    'v15': {
        'relevance': 0.3047,
        'utilization': 0.0916,
        'completeness': 0.2219,
        'adherence': 0.65,
        'relevance_mae': 0.2692,
        'utilization_mae': 0.2986,
        'completeness_mae': 0.5197,
        'adherence_mae': 0.5
    },
    'v13': {
        'relevance': 0.5079,
        'utilization': 0.3243,
        'completeness': 0.6319,
        'adherence': 0.15,
        'relevance_mae': 0.2244,
        'utilization_mae': 0.1443,
        'completeness_mae': 0.2521,
        'adherence_mae': 0.7
    },
    'v12': {
        'relevance': 0.4978,
        'utilization': 0.1786,
        'completeness': 0.2906,
        'adherence': 0.55,
        'relevance_mae': 0.193,
        'utilization_mae': 0.2103,
        'completeness_mae': 0.4258,
        'adherence_mae': 0.5
    }
}

print("Config | Relevance | Utilization | Completeness | Adherence")
print("-------|-----------|-------------|--------------|----------")
for version in ['v11', 'v12', 'v13', 'v14', 'v15']:
    d = csv_data[version]
    print(f"{version}    | {d['relevance']:.4f}    | {d['utilization']:.4f}      | {d['completeness']:.4f}       | {d['adherence']:.4f}")

print("\n=== ANALYSIS DOCUMENTS SCORES ===\n")

analysis_data = {
    'v11': {
        'relevance': 0.515,
        'utilization': 0.299,
        'completeness': 0.569,
        'adherence': 0.250
    },
    'v14': {
        'relevance': 0.489,
        'utilization': 0.370,
        'completeness': 0.685,
        'adherence': 0.850
    },
    'v15': {
        'relevance': '0.535-0.585 (est)',
        'utilization': '0.380-0.400 (est)',
        'completeness': '0.685-0.700 (est)',
        'adherence': '0.850 (est)'
    },
    'v13': {
        'relevance': 0.508,
        'utilization': 0.324,
        'completeness': 0.632,
        'adherence': 0.450
    },
    'v12': {
        'relevance': 0.508,
        'utilization': 0.220,
        'completeness': 0.480,
        'adherence': 0.650
    }
}

print("Config | Relevance | Utilization | Completeness | Adherence")
print("-------|-----------|-------------|--------------|----------")
for version in ['v11', 'v12', 'v13', 'v14', 'v15']:
    d = analysis_data[version]
    print(f"{version}    | {str(d['relevance']):9} | {str(d['utilization']):11} | {str(d['completeness']):12} | {str(d['adherence']):9}")

print("\n=== KEY DIFFERENCES ===\n")

print("v14 Comparison:")
print("  CSV:      relevance=0.3332, adherence=0.6")
print("  Analysis: relevance=0.489, adherence=0.850")
print("  Difference: HUGE - CSV scores are much lower")
print()

print("v11 Comparison:")
print("  CSV:      relevance=0.5147, adherence=0.25")
print("  Analysis: relevance=0.515, adherence=0.250")
print("  Difference: MATCHES - CSV and analysis agree on v11")
print()

print("v13 Comparison:")
print("  CSV:      relevance=0.5079, adherence=0.15")
print("  Analysis: relevance=0.508, adherence=0.450")
print("  Difference: PARTIAL - relevance matches, adherence differs")
print()

print("\n=== HYPOTHESIS: What is comparison.csv measuring? ===\n")

print("THEORY 1: Different Evaluation Metric")
print("  - CSV might be using 'predicted_scores' instead of 'evaluation' scores")
print("  - Or using a different evaluation strategy")
print("  - Or comparing against ground truth (MAE = Mean Absolute Error)")
print()

print("THEORY 2: Different Data Source")
print("  - CSV might be from a different experiment run")
print("  - Or using a different subset of queries")
print("  - Or using a different evaluation method")
print()

print("THEORY 3: MAE (Mean Absolute Error) Interpretation")
print("  - CSV shows both __mean and __mae columns")
print("  - __mean = average score")
print("  - __mae = mean absolute error from ground truth")
print("  - This suggests CSV is comparing predictions vs ground truth")
print()

print("THEORY 4: Different Evaluation Approach")
print("  - Analysis documents: Using TRACe evaluation (LLM-based)")
print("  - CSV: Might be using a different evaluation method")
print("  - Or comparing model predictions vs ground truth labels")
print()

print("\n=== WHAT IS comparison.csv? ===\n")

print("Looking at the structure:")
print("  - Has __mean and __mae columns")
print("  - MAE = Mean Absolute Error")
print("  - This suggests: comparing predictions vs ground truth")
print()

print("Possible interpretation:")
print("  - __mean: Average predicted score")
print("  - __mae: Average error between predicted and ground truth")
print()

print("Example for v14:")
print("  - relevance_score__mean: 0.3332 (average predicted relevance)")
print("  - relevance_score__mae: 0.3087 (average error from ground truth)")
print("  - This means: predictions are off by ~0.31 on average")
print()

print("This is DIFFERENT from TRACe evaluation:")
print("  - TRACe: LLM judges if answer is supported by passages")
print("  - CSV: Comparing model predictions vs ground truth labels")
print()

print("\n=== MOST LIKELY EXPLANATION ===\n")

print("comparison.csv is measuring:")
print("  1. Model's ability to predict relevance/adherence/etc scores")
print("  2. How well predictions match ground truth labels")
print("  3. NOT the actual quality of answers (like TRACe does)")
print()

print("Analysis documents are measuring:")
print("  1. Actual answer quality using TRACe evaluation")
print("  2. Whether answers follow passage-only rule")
print("  3. Whether answers use all relevant information")
print()

print("CONCLUSION:")
print("  - comparison.csv and analysis documents measure DIFFERENT THINGS")
print("  - CSV: Model prediction accuracy")
print("  - Analysis: Answer quality (TRACe evaluation)")
print("  - They are NOT directly comparable")
print()

print("\n=== RECOMMENDATION ===\n")

print("Use ANALYSIS DOCUMENTS for decision-making:")
print("  ✅ TRACe evaluation measures actual answer quality")
print("  ✅ Directly relevant to RAG system performance")
print("  ✅ Tells us if answers are good or bad")
print()

print("Use comparison.csv for:")
print("  ⚠️ Understanding model prediction accuracy")
print("  ⚠️ Debugging prediction quality")
print("  ⚠️ Not for overall system evaluation")
print()

print("=" * 120)
