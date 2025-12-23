#!/bin/bash
# Wait for PostgreSQL to be ready

# Install PostgreSQL client tools required for pg_isready
apt-get update -y
apt-get install -y postgresql-client
rm -rf /var/lib/apt/lists/*

echo "Waiting for PostgreSQL service (db:5432)..."

# Use environment variables set by Docker Compose
until PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h db -p 5432 -U $POSTGRES_USER -d $POSTGRES_DB -t 1; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up and running! Proceeding with migration."
