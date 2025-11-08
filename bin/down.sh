#!/bin/bash

# rm frontend build files
cd frontend
rm -r dist
rm -r node_modules

# take down image
cd ../backend
docker compose down

# stop backend
systemctl stop mathmex-backend

# move back to root
cd ..