#!/bin/bash
DB_HOST=postgres
DB_PORT=5432

echo "Waiting for Postgres at ${DB_HOST}:${DB_PORT}..."
while ! nc -z ${DB_HOST} ${DB_PORT}; do
  sleep 0.1
done
echo "Postgres started successfully!"

echo "Running database migrations..."
alembic upgrade head

exec "$@"