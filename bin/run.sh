#!/bin/bash
# Run from project root. Starts OpenSearch and backend.

set -e
cd "$(dirname "$0")/.."

# OpenSearch (--env-file loads OPENSEARCH_INITIAL_ADMIN_PASSWORD from project root)
(cd apps/opensearch && docker compose --env-file ../../.env up -d)

# Backend (systemd in prod; for dev run: python apps/backend/app.py)
systemctl start mathmex-backend 2>/dev/null || echo "Run backend manually: python apps/backend/app.py"