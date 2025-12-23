# ==========================================
# STAGE 1: Backend Builder (Python)
# ==========================================
FROM python:3.12-slim AS backend-builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Fix: Pointing to the internal subfolder for the Common SDK
COPY Agent_Nexus-v2-main/common/ /app/common/
RUN pip install --no-cache-dir ./common

# Install dependencies for all Lobes to prevent missing module errors in Stage 3
COPY Agent_Nexus-v2-main/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: Frontend Builder (Next.js)
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app
# Fix: Pointing to your specific frontend folder name
COPY agent_nexus_frontend/package*.json ./
RUN npm ci

COPY agent_nexus_frontend/ . 
RUN npm run build

# ==========================================
# STAGE 3: Final Production Runner
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app
# Install curl for the HEALTHCHECK
RUN apt-get update && apt-get install -y curl libpq5 && rm -rf /var/lib/apt/lists/*
RUN groupadd -r nexus && useradd -r -g nexus nexus

COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Frontend Artifacts
COPY --from=frontend-builder /app/.next/standalone ./frontend
COPY --from=frontend-builder /app/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/public ./frontend/public

# Fix: Copying from the subfolder but flattening into /app/
COPY Agent_Nexus-v2-main/ /app/

RUN chown -R nexus:nexus /app
USER nexus

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Launch the Gateway (The entry point for all 4 Lobes)
ENTRYPOINT ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]