# MathMex Data Processing

Transforms raw TSVs into JSONL ready for indexing (vector embeddings, formula extraction). See the [main README](../../README.md) for full project setup.

## Quick Start

From project root:

```sh
bin/process.sh SOURCE TSV_FILE [--index]
```

Example: `bin/process.sh wikipedia final_wikipedia.tsv --index`

## Scripts

| Script | Purpose |
|--------|---------|
| `generate_vectors.py` | TSV → vector embeddings (.npy) |
| `generate_jsonl.py` | TSV + vectors → JSONL |

Run from project root:

```sh
python apps/data-processing/generate_vectors.py SOURCE TSV_FILE
python apps/data-processing/generate_jsonl.py SOURCE TSV_FILE
```

## Data Layout

Output goes to `data/` at project root (gitignored):

```
data/
├── tsvs/      # Input: title<TAB>description<TAB>url (no header)
├── vectors/   # Generated .npy embeddings
└── jsonl/     # Output for bulk_index.py
```

## TSV Format

One row per document, tab-separated, no header:

```
title	body text or description	url
```

## Pipeline

1. Add TSV to `data/tsvs/`
2. `bin/process.sh SOURCE TSV_FILE` (or run generate_vectors + generate_jsonl)
3. `python apps/opensearch/scripts/bulk_index.py SOURCE`
