# LuminaLib – Intelligent Library System

> AI-powered library management system built with FastAPI, Next.js, PostgreSQL, local LLM via Ollama.

---

## Prerequisites

 Tool | Version 
 Docker | ≥ 24.x 
 Docker Compose | ≥ 2.x 

---

## One-Command Start

```bash
# 1. Clone the repository
git clone <repo-url> luminalib && cd luminalib

# 2. Copy environment file
cp .env.example .env   # optionally edit secrets

# 3. Build and up everything
docker compose up --build
```

Docker Compose will:

1. Boot **PostgreSQL** and run the init SQL.
4. Boot **Ollama** and pull `llama3.2:1b` (≈3.5 GB download on first run).
5. Boot the **Background worker** for background LLM tasks.
6. Boot the **FastAPI** backend and run Alembic migrations.
7. Boot the **Next.js** frontend.

### Service URLs

 Service | URL 
 Frontend | http://localhost:3000 
 API | http://localhost:8000 
 API Docs (Swagger) | http://localhost:8000/docs 
 Ollama | http://localhost:11434 

---

## Configuration

All configuration is via the `.env` file and Settings Class (Pydantic).

### Swap Storage Backend

```env
STORAGE_BACKEND=s3      # AWS S3 (set AWS_* vars too)
STORAGE_BACKEND=local   # filesystem (tests only)
```

### Swap LLM Provider

```env
LLM_BACKEND=ollama      # local Ollama (default)
LLM_BACKEND=openai      # OpenAI API (set OPENAI_API_KEY)
```

No code changes required — just `.env` edits.

---

## Development Workflow

### Backend

```bash
cd backend

# Install locally (optional, for IDE support)
pip install -r requirements.txt

# Lint
ruff check app/
mypy app/

# Run migrations manually
alembic upgrade head

# Tests
pytest tests/
```

### Migrations
#alembic
migrations are hanlded automatically by the backend container on startup, but you can also run them manually if needed:
```bash
alembic upgrade head
```


### Frontend

```bash
cd frontend

npm install

# Dev server (hot reload)
npm run dev

# Test
npm run test

# Lint
npm run lint
```

---

## API Reference

Full docs: http://localhost:8000/docs

## Run without Docker

1. PostgreSQL running; create database and user (e.g. `luminalib`).
2. Backend: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && npm install && npm run dev`
4. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the frontend.

See `ARCHITECTURE.md` for schema, async LLM, recommendation logic, and frontend design.


