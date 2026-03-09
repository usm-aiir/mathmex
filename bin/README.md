# MathMex Bin

Shell scripts for managing the application. Run from project root. See the [main README](../README.md) for full instructions.

## Scripts

| Script | Purpose |
|--------|---------|
| `run.sh` | Start OpenSearch + backend |
| `stop.sh` | Stop services, remove build artifacts |
| `install.sh` | Build frontend and OpenSearch image |
| `restart.sh` | Stop → install → run |
| `process.sh` | Process data (vectors → JSONL), optionally index |

## Usage

```sh
bin/install.sh
bin/run.sh
bin/stop.sh
bin/restart.sh

bin/process.sh SOURCE TSV_FILE [--index]
```
