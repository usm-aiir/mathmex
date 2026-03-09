# MathMex Backend

Flask API server that handles search requests and talks to OpenSearch. See the [main README](../../README.md) for full project setup.

## Run

From project root:

```sh
python apps/backend/app.py
```

Or use `bin/run.sh` to start OpenSearch and the backend together.

## Configuration

Reads `config.ini` at project root (or path in `BACKEND_CONFIG` env var). Required sections:

- **[opensearch]** — Host, username, password
- **[flask_app]** — Port (default 5001), debug
- **[general]** — Sentence-transformers model path

## Structure

- `app.py` — Flask app entry point
- `routes/` — API endpoints (search, fusion, utility)
- `services/` — OpenSearch client, model loading
- `schemas/` — Source-to-index mappings
- `utils/` — Formatting, helpers

## Dependencies

See `requirements.txt`. Install with `pip install -r requirements.txt` (from project root or this directory).
