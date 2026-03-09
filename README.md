# MathMex

MathMex is a web application for mathematical search, powered by OpenSearch and machine learning. It consists of a Flask backend, React frontend, and a data pipeline that transforms TSVs into searchable indices.

## Prerequisites

- **Python 3.8+** — Backend and data pipeline
- **Node.js 18+** — Frontend
- **Docker** — OpenSearch (or use a remote instance)
- **formula-search** (optional) — For TangentCFT/formula search; add as git submodule

## Project Structure

```
mathmex/
├── apps/
│   ├── backend/        # Flask API server
│   ├── data-processing/  # TSV → vectors → JSONL pipeline
│   ├── opensearch/     # OpenSearch scripts, schemas, docker-compose
│   └── frontend/       # React UI
├── bin/                # Shell scripts (run, stop, install, process)
└── data/               # TSVs, vectors, JSONL (gitignored)
```

See each app's README for details: [backend](apps/backend/README.md), [data-processing](apps/data-processing/README.md), [opensearch](apps/opensearch/README.md), [frontend](apps/frontend/README.md).

## Getting Started

**Run all commands from the project root.**

### 1. Configuration

```sh
cp config.ini.example config.ini
cp .env.example .env
```

Edit `config.ini`:

- **[opensearch]** — Host, username, password. For local Docker, use `host = localhost` and credentials matching your `.env`.
- **[general]** — `model` = path to sentence-transformers model (local path or HuggingFace ID, e.g. `sentence-transformers/all-mpnet-base-v2`).

Edit `.env`:

- **`OPENSEARCH_INITIAL_ADMIN_PASSWORD`** — Bootstrap password for the OpenSearch container. The `bin/` scripts pass this via `--env-file` when running docker compose. Set `config.ini` [opensearch] password to match.
- **`VITE_API_BASE`** — (Optional) For local frontend dev, set to `http://localhost:5001` to point at the backend. Omit for production.

### 2. Install

```sh
bin/install.sh
```

This builds the frontend and OpenSearch Docker image.

### 3. Run

Start OpenSearch and the backend:

```sh
bin/run.sh
```

Or manually:

```sh
cd apps/opensearch && docker compose --env-file ../../.env up -d
python apps/backend/app.py
```

(The `--env-file` loads `OPENSEARCH_INITIAL_ADMIN_PASSWORD` from `.env`.)

Start the frontend (dev mode):

```sh
cd apps/frontend && npm run dev
```

Open the app (typically http://localhost:5173 for Vite).

### 4. Data Pipeline

To add searchable content:

1. Add a TSV to `data/tsvs/` (format: `title<TAB>description<TAB>url`, no header).
2. Run: `bin/process.sh SOURCE TSV_FILE`
3. Index: `python apps/opensearch/scripts/bulk_index.py SOURCE`

Or combine steps 2 and 3: `bin/process.sh SOURCE TSV_FILE --index`

Example: `bin/process.sh wikipedia final_wikipedia.tsv --index`

### 5. formula-search (Optional)

For full search (TangentCFT, LateFusion), add the formula-search repo as a submodule.

**First-time setup** (run from project root):

If you have an existing formula-search copy with generated files (encoded.jsonl, slt_index.faiss, etc.) and want to convert it to a submodule without re-running the formula-search pipeline:

```sh
bin/setup_formula_search_submodule.sh <formula-search-repo-url>
```

This backs up generated files, adds the submodule, then restores them. For private repos, ensure git auth is configured first (e.g. `git config credential.helper store` or use SSH URL).

Or, for a fresh setup:

```sh
git submodule add <formula-search-repo-url> formula-search
git submodule update --init --recursive
```

**Clone mathmex with submodule**:

```sh
git clone --recurse-submodules <mathmex-repo-url>
```

**Existing clone** (submodule not initialized):

```sh
git submodule update --init --recursive
```

## Commands Reference

| Command | Purpose |
|---------|---------|
| `bin/install.sh` | Build frontend and OpenSearch image |
| `bin/run.sh` | Start OpenSearch + backend |
| `bin/stop.sh` | Stop services, remove build artifacts |
| `bin/restart.sh` | Stop → install → run |
| `bin/process.sh SOURCE TSV [--index]` | Process data, optionally index |
| `python apps/backend/app.py` | Run backend only |
| `python apps/opensearch/scripts/bulk_index.py SOURCE` | Bulk index JSONL |
| `cd apps/frontend && npm run dev` | Frontend dev server |

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b my-feature`
3. Make changes; tests are encouraged
4. Commit: `git commit -m "Description"`
5. Push: `git push origin my-feature`
6. Open a Pull Request
