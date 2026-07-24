"""Check cache metadata and chunk contents."""
import json
import pickle
from pathlib import Path

cache_dir = Path("cache")

print("=== CHUNK CACHE METADATA ===")
for meta_file in sorted(cache_dir.glob("chunks/*/metadata.json")):
    with open(meta_file) as f:
        meta = json.load(f)
    print(f"\n  Cache: {meta_file.parent.name[:16]}...")
    for k, v in meta.items():
        print(f"    {k}: {v}")

print("\n=== CHUNK CONTENT SAMPLE ===")
for pkl_file in sorted(cache_dir.glob("chunks/*/chunks.pkl")):
    with open(pkl_file, 'rb') as f:
        chunks = pickle.load(f)
    print(f"\n  Cache: {pkl_file.parent.name[:16]}... ({len(chunks)} chunks)")
    if chunks:
        c = chunks[0]
        print(f"    First chunk text[:120]: {c.text[:120]}")
        print(f"    First chunk parser_type: {c.metadata.get('parser_type', 'N/A')}")
        print(f"    First chunk sample_index: {c.metadata.get('sample_index', 'N/A')}")
        # Check a chunk from middle
        mid = len(chunks) // 2
        c2 = chunks[mid]
        print(f"    Mid chunk text[:120]: {c2.text[:120]}")
        print(f"    Mid chunk parser_type: {c2.metadata.get('parser_type', 'N/A')}")
        print(f"    Mid chunk sample_index: {c2.metadata.get('sample_index', 'N/A')}")

print("\n=== EMBEDDING CACHE METADATA ===")
for meta_file in sorted(cache_dir.glob("embeddings/*/metadata.json")):
    with open(meta_file) as f:
        meta = json.load(f)
    print(f"\n  Cache: {meta_file.parent.name[:16]}...")
    for k, v in meta.items():
        print(f"    {k}: {v}")

print("\n=== INDEX CACHE METADATA ===")
for meta_file in sorted(cache_dir.glob("indexes/*/metadata.json")):
    with open(meta_file) as f:
        meta = json.load(f)
    print(f"\n  Cache: {meta_file.parent.name[:16]}...")
    for k, v in meta.items():
        print(f"    {k}: {v}")
