"""Check if cache is stale / built from old parser."""
import json
import hashlib
from pathlib import Path

cache_dir = Path("cache")
print("=== CACHE DIRECTORY ===")
for p in sorted(cache_dir.rglob("*")):
    if p.is_file():
        size_kb = p.stat().st_size / 1024
        print(f"  {p.relative_to(cache_dir)} ({size_kb:.1f} KB)")

# Check chunk cache contents
print("\n=== CHUNK CACHE INSPECTION ===")
chunk_files = list(cache_dir.rglob("*chunk*"))
if not chunk_files:
    chunk_files = list(cache_dir.rglob("*.json"))

for cf in chunk_files[:5]:
    print(f"\n  File: {cf}")
    try:
        with open(cf) as f:
            data = json.load(f)
        if isinstance(data, dict):
            print(f"  Keys: {list(data.keys())[:10]}")
            # Look for metadata about parser type
            if 'metadata' in data:
                print(f"  Metadata: {data['metadata']}")
            if 'chunks' in data and len(data['chunks']) > 0:
                first_chunk = data['chunks'][0]
                if isinstance(first_chunk, dict):
                    meta = first_chunk.get('metadata', {})
                    text_preview = first_chunk.get('text', '')[:100]
                    print(f"  First chunk parser_type: {meta.get('parser_type', 'N/A')}")
                    print(f"  First chunk text: {text_preview}...")
        elif isinstance(data, list) and len(data) > 0:
            first = data[0]
            if isinstance(first, dict):
                meta = first.get('metadata', {})
                text_preview = first.get('text', '')[:100]
                print(f"  First item parser_type: {meta.get('parser_type', 'N/A')}")
                print(f"  First item text: {text_preview}...")
    except Exception as e:
        print(f"  Error reading: {e}")
