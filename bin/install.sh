#!/bin/bash

# frontend
cd apps/frontend
npm install
npm run build

# db
cd ../db
docker compose build

# move back to root
cd ../..