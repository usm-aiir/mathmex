#!/bin/bash

# frontend
cd apps/frontend
npm install
npm run build

# opensearch
cd ../opensearch
docker compose --env-file ../../.env build

# move back to root
cd ../..