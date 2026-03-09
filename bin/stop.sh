#!/bin/bash

# rm frontend build files
cd apps/frontend
rm -r dist
rm -r node_modules

# take down image
cd ../opensearch
docker compose --env-file ../../.env down

# stop backend
systemctl stop mathmex-backend

# move back to root
cd ../..