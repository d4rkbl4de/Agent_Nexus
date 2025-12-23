FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FASTAPI_ENV=production

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-openbsd \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN pip install -e ./common

RUN chmod +x prestart.sh

ENTRYPOINT ["/bin/bash", "prestart.sh"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]