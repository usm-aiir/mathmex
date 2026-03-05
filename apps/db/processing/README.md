# MathMex Data Processing

This directory contains scripts used to generate and process data for indexing into the MathMex OpenSearch database.

Raw data files (TSVs, NumPy vectors, and JSONL output) are stored in the repo-level `data/` directory, not here. See the layout below.

---

## Scripts

- **`generate_vectors.py`** — Reads raw TSV files and generates vector embeddings (`.npy`) using the sentence transformer model and TangentCFT for formula vectors.
- **`generate_jsonl.py`** — Combines `.tsv` metadata with the generated `.npy` vectors into a `.jsonl` file ready for bulk indexing.

---

## Data Layout (`data/` at repo root)

```
data/
├── tsvs/        # Raw input: title<TAB>description<TAB>url (no header row)
├── vectors/     # Generated .npy embeddings (content, text, formula vectors + index)
└── jsonl/       # Final output .jsonl files ready for bulk_index.py
```

The `data/` directory is gitignored — files must be generated locally before indexing.

---

## Pipeline

1. **Prepare raw data** — Add one or more `.tsv` files to `data/tsvs/` formatted as:
   ```
   title<TAB>description<TAB>url
   ```
   No header row. Set `SOURCE` and `TSV_FILE` at the top of both scripts to match.

2. **Generate vectors** — Run from this directory:
   ```sh
   python generate_vectors.py
   ```
   Outputs `.npy` files to `data/vectors/`.

3. **Combine and export** — Run:
   ```sh
   python generate_jsonl.py
   ```
   Outputs a `.jsonl` file to `data/jsonl/`. Ensure the `media_type` field at the top of the script matches the source.

4. **Bulk index** — Run `bulk_index.py` from `apps/db/admin/` to upload the `.jsonl` to OpenSearch.