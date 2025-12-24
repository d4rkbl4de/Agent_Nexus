#!/bin/bash

set -e

echo "PRESTART: Checking Database Connectivity..."
python << END
import sys
import psycopg2
import os
try:
    psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", 5432)
    )
except Exception as e:
    print(f"Database not ready: {e}")
    sys.exit(-1)
END

echo "PRESTART: Running Alembic Migrations..."
alembic upgrade head

echo "PRESTART: Initializing Vector Store Collections..."
python -m scripts.init_vector_db

echo "PRESTART: Completed successfully. Handing over to Application..."
exec "$@"