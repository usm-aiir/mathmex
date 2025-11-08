#!/bin/bash

# frontend
cd frontend
npm install
npm run build

# db
cd ../backend
docker compose build

# move back to root
cd ..