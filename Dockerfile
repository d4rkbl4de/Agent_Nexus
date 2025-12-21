FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV FASTAPI_ENV production

# Install system dependencies (needed for netcat and Postgres connection)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code (including all four lobes and common/ SDK)
COPY . /app

# Run pre-start script to wait for DBs and run migrations
ENTRYPOINT ["/bin/bash", "prestart.sh"]

# Command to run the unified FastAPI application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]