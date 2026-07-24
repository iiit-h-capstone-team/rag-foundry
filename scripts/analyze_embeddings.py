"""Test whether BGE-large can actually match queries to correct docs."""
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# Load chunks
with open('cache/chunks/62e5db710580f21d3b448009918d5b39c7a1a7ad75fa50e0b2ef87ddfd8b8e9a/chunks.pkl', 'rb') as f:
    chunks = pickle.load(f)

print(f"Total chunks: {len(chunks)}")

# Group chunks by sample_index
sample_chunks = {}
for c in chunks:
    si = c.metadata.get('sample_index', -1)
    sample_chunks.setdefault(si, []).append(c)

# Load dataset for queries
from datasets import load_dataset
ds = load_dataset('galileo-ai/ragbench', 'covidqa', split='test')

# Load embedding model
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# Test Q1: "When was the first case of COVID-19 identified?"
query = ds[1]['question']
print(f"\nQuery: {query}")

# Embed query
q_emb = model.encode([query], normalize_embeddings=True)

# Embed all chunks and find top-10 by cosine sim
all_texts = [c.text for c in chunks]
all_embs = model.encode(all_texts, normalize_embeddings=True, show_progress_bar=True, batch_size=64)

sims = np.dot(all_embs, q_emb.T).flatten()
top_indices = np.argsort(sims)[::-1][:10]

print("\nTop 10 most similar chunks:")
for rank, idx in enumerate(top_indices):
    c = chunks[idx]
    si = c.metadata.get('sample_index', -1)
    sim = sims[idx]
    print(f"  #{rank+1} sim={sim:.4f} sample={si}: {c.text[:100]}...")

# Show correct docs (sample 1)
print(f"\nCorrect docs (sample 1):")
for c in sample_chunks.get(1, []):
    idx = chunks.index(c)
    sim = sims[idx]
    print(f"  sim={sim:.4f}: {c.text[:100]}...")

# Repeat for Q0
query0 = ds[0]['question']
q0_emb = model.encode([query0], normalize_embeddings=True)
sims0 = np.dot(all_embs, q0_emb.T).flatten()
top0 = np.argsort(sims0)[::-1][:10]

print(f"\n\nQuery: {query0}")
print("Top 10:")
for rank, idx in enumerate(top0):
    c = chunks[idx]
    si = c.metadata.get('sample_index', -1)
    print(f"  #{rank+1} sim={sims0[idx]:.4f} sample={si}: {c.text[:100]}...")

print(f"\nCorrect docs (sample 0):")
for c in sample_chunks.get(0, []):
    idx = chunks.index(c)
    print(f"  sim={sims0[idx]:.4f}: {c.text[:100]}...")
