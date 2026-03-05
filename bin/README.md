# MathMex Bin

The `bin` directory contains shell scripts for managing the MathMex application on the host server. All scripts should be run from the repo root.

## Scripts

| Script | Purpose |
|---|---|
| `run.sh` | Start the backend Docker container and systemd service |
| `stop.sh` | Stop the backend and remove frontend build artifacts |
| `install.sh` | Build the frontend and rebuild the backend Docker image |
| `restart.sh` | Full stop → install → run cycle |

## Usage

```sh
sudo bin/run.sh       # start the application
sudo bin/stop.sh      # stop the application
sudo bin/install.sh   # rebuild after code changes
sudo bin/restart.sh   # rebuild and restart
```