# ==========================================
# STAGE 1: Backend Builder (Python)
# ==========================================
FROM python:3.12-slim AS backend-builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Common SDK & Global Deps
COPY common/ /app/common/
RUN pip install --no-cache-dir ./common

# Install Lobe dependencies (Example: InsightMate)
COPY InsightMate/requirements.txt /app/InsightMate/
RUN pip install --no-cache-dir -r /app/InsightMate/requirements.txt

# ==========================================
# STAGE 2: Frontend Builder (Next.js)
# ==========================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ . 
# Enable standalone output in next.config.js for Phase 6
RUN npm run build

# ==========================================
# STAGE 3: Final Production Runner
# ==========================================
FROM python:3.12-slim AS runner

WORKDIR /app
RUN groupadd -r nexus && useradd -r -g nexus nexus

# Copy Python Environment from Stage 1
COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy Frontend Static Artifacts from Stage 2
# (In Phase 6, we serve frontend via Nginx or FastAPI StaticFiles)
COPY --from=frontend-builder /app/.next/standalone ./frontend
COPY --from=frontend-builder /app/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/public ./frontend/public

# Copy Lobe Code
COPY InsightMate/ /app/InsightMate/
COPY scripts/ /app/scripts/

# Security: Run as non-root
RUN chown -R nexus:nexus /app
USER nexus

EXPOSE 8000

# Healthcheck to ensure the "Brain" is alive
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["python", "-m", "uvicorn", "InsightMate.main:app", "--host", "0.0.0.0", "--port", "8000"]