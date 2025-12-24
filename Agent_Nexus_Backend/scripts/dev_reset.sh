#!/usr/bin/env bash
set -e

docker compose down -v
docker compose up -d db
sleep 5
alembic upgrade head
python scripts/seed_data.py
