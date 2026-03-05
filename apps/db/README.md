# MathMex DB

This directory contains everything needed to set up, populate, and manage the MathMex OpenSearch database.

## Structure

```
db/
├── admin/        # Scripts to manage OpenSearch indices
├── processing/   # Scripts to generate and prepare data for indexing
└── schemas/      # Index name mappings and shared schema definitions
```

## Subdirectories

### `admin/`

One-off scripts for managing OpenSearch indices. Run these from the `admin/` directory. All scripts read connection credentials from `apps/backend/config.ini`.

| Script | Purpose |
|---|---|
| `create_index.py` | Create a new index with the MathMex mapping |
| `delete_index.py` | Delete an index and all its data |
| `clear_index.py` | Remove all documents from an index (keeps the index) |
| `bulk_index.py` | Bulk upload a `.jsonl` file into an index |

### `processing/`

Scripts to transform raw data into a format ready for indexing. See [`processing/README.md`](processing/README.md) for the full pipeline walkthrough.

### `schemas/`

Shared Python definitions used across admin and processing scripts, including the `source_to_index` mapping in `indexes.py`.

## Configuration

Admin scripts expect a `config.ini` file at `apps/backend/config.ini` with the following sections:

```ini
[opensearch]
host = ...
username = ...
password = ...

[flask_app]
port = ...
debug = ...

[general]
model = ...
```
