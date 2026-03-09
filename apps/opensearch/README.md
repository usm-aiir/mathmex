# MathMex OpenSearch

OpenSearch index management: scripts, schemas, and docker-compose. See the [main README](../../README.md) for full project setup.

## Run OpenSearch (Docker)

From project root. Requires `.env` with `OPENSEARCH_INITIAL_ADMIN_PASSWORD` (see [main README](../../README.md)):

```sh
cd apps/opensearch && docker compose --env-file ../../.env up -d
```

Or use `bin/run.sh` to start OpenSearch and the backend together (it passes `--env-file` automatically).

## Scripts

Run from project root. All scripts read `config.ini` at project root.

| Script | Purpose |
|--------|---------|
| `python apps/opensearch/scripts/bulk_index.py SOURCE` | Bulk upload JSONL to an index |
| `python apps/opensearch/scripts/create_index.py` | Create an index (edit `INDEX_NAME` in script) |
| `python apps/opensearch/scripts/delete_index.py` | Delete an index (edit `INDEX_NAME` in script) |
| `python apps/opensearch/scripts/clear_index.py` | Clear documents from an index (edit `INDEX_NAME` in script) |

## Structure

```
opensearch/
├── scripts/      # bulk_index, create_index, delete_index, clear_index
├── schemas/      # indexes.py (source→index), mappings.py (index structure)
└── docker-compose.yml
```

## Configuration

- **Scripts** — Use `config.ini` at project root.
- **Docker** — Uses `OPENSEARCH_INITIAL_ADMIN_PASSWORD` from `.env` (via `--env-file` in `bin/` scripts). See [main README](../../README.md) for setup.
