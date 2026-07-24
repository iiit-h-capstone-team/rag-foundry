"""Deep analysis: why retrieval misses correct documents entirely."""
import json

# Load report
with open('reports/covidqa_title_aware_v1.json') as f:
    report = json.load(f)

section = report['sections'][0]

# Load raw dataset to compare ground truth docs
from datasets import load_dataset
ds = load_dataset('galileo-ai/ragbench', 'covidqa', split='test')

print("=== DATASET INFO ===")
print(f"  Total samples: {len(ds)}")
print(f"  Columns: {ds.column_names}")
print(f"  Sample 0 docs count: {len(ds[0]['documents'])}")
print()

# For first 3 queries, compare ground truth docs vs retrieved docs
for qi in range(3):
    q = section['per_query'][qi]
    query = q['query']
    gt_docs = ds[qi]['documents']

    print(f"=== Q{qi}: {query[:80]} ===")
    print(f"  Ground truth: {len(gt_docs)} documents from sample {qi}")
    for j, doc in enumerate(gt_docs):
        print(f"    GT doc {j}: {doc[:100]}...")

    print(f"  Retrieved: {len(q['retrieved_documents'])} documents")
    for j, doc in enumerate(q['retrieved_documents']):
        si = doc.get('metadata', {}).get('sample_index', '?')
        content = doc.get('content', doc.get('text', ''))[:100]
        print(f"    Ret doc {j} (sample={si}): {content}...")
    print()

# Check total indexed docs
all_samples = set()
for q in section['per_query']:
    for doc in q.get('retrieved_documents', []):
        all_samples.add(doc.get('metadata', {}).get('sample_index', -1))
print(f"=== INDEX COVERAGE ===")
print(f"  Unique sample indices seen in retrieved docs: {len(all_samples)}")
print(f"  Sample indices 0-19 in retrieved: {sorted(s for s in all_samples if s < 20)}")
print(f"  All sample indices: {sorted(all_samples)[:30]}...")
