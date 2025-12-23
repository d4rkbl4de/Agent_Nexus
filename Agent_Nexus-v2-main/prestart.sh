#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Waiting for Postgres to wake up..."

# Use pg_isready to check if the DB is ready
# 'db' is the service name in your docker-compose.yml
while ! pg_isready -h db -U agentnexus_user -d agentnexus_db; do
  sleep 1
done

echo "Postgres is awake! Running migrations..."

# Run Alembic migrations from the common SDK or specific lobe
# This ensures your tables (User, ChatHistory) exist before the app starts
alembic upgrade head

echo "Migrations complete. Starting the Lobe..."

exec "$@"