#!/usr/bin/env python3
"""Test script to verify noop parser works with chunking."""

from datasets import load_dataset
from parsers import parser_registry, ParserType
from data_sources.processors import DataProcessor
from rag.modules.chunking.registry import chunking_registry
from rag.modules.chunking.strategies.sentence.config import SentenceChunkingConfig

# Load a small sample from PubMedQA
print('Loading PubMedQA sample...')
dataset = load_dataset('galileo-ai/ragbench', name='pubmedqa', split='test')
sample = dataset[0]

# Get raw documents
raw_docs = sample.get('documents', [])
print(f'Raw documents count: {len(raw_docs)}')
print(f'First document length: {len(raw_docs[0])} chars')

# Test noop parser
print('\nTesting noop parser...')
parser = parser_registry.create('noop')
processor = DataProcessor(parser_strategy=parser)

# Create mock dataset format
mock_dataset = [{'documents': raw_docs}]
documents = processor.process_dataset(mock_dataset)

print(f'Parsed {len(documents)} documents')
print(f'Document 0 title: {repr(documents[0].title)}')
print(f'Document 0 content length: {len(documents[0].content)} chars')

# Test chunking
print('\nTesting chunking with parsed documents...')
chunker = chunking_registry.create('sentence', config=SentenceChunkingConfig())
chunks = chunker.chunk(documents[0])

print(f'Created {len(chunks)} chunks from first document')
print(f'\nChunk 0 preview: {chunks[0].text[:100]}...')
print(f'Chunk 0 metadata: {chunks[0].metadata}')

print('\n✅ SUCCESS: Chunking works properly with noop parser!')
