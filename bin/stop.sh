#!/bin/bash

# rm frontend build files
cd apps/frontend
rm -r dist
rm -r node_modules

# take down image
cd ../db
docker compose down

# stop backend
systemctl stop mathmex-backend

# move back to root
cd ../..