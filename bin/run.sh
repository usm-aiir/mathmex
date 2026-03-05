#!/bin/bash

# Start OpenSearch database
cd apps/db
docker compose up -d
cd ../..

# Start backend service
systemctl start mathmex-backend