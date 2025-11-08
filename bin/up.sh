#!/bin/bash

# backend run cmd
cd backend
docker compose up -d

# ensure backend is running
systemctl start mathmex-backend

# move back to root
cd ..