FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl libpq-dev poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system lumina \
    && adduser --system --ingroup lumina lumina \
    && chown -R lumina:lumina /app

USER lumina

EXPOSE 8000

