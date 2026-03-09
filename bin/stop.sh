#!/bin/bash

# rm frontend build files (ignore if missing)
cd apps/frontend
rm -rf dist node_modules 2>/dev/null || true

# take down OpenSearch (graceful shutdown first to preserve indexed data)
cd ../opensearch
docker compose --env-file ../../.env down
# remove orphaned containers that block recreate (e.g. from previous runs)
docker rm -f opensearch-dashboards opensearch-node 2>/dev/null || true

# stop backend
systemctl stop mathmex-backend

# move back to root
cd ../..