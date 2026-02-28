# LuminaLib – Library System


## Prerequisites

Tool | Version 
Docker | ≥ 24.x 
Docker Compose | ≥ 2.x
(Optional) NVIDIA GPU | For faster LLM inference |

## One-Command Start

```bash
# 1. Start everything
docker compose up --build
```

**That's it.** Docker Compose will:

1. Boot **PostgreSQL** and run the init SQL.
2 Boot **Ollama** and pull `llama3.2:1b` (≈3.5 GB download on first run).
3. Boot the **FastAPI** backend and run Alembic migrations.
4. Boot the **Next.js** frontend.

### Service URLs

Service | URL 
_____________
Frontend | http://localhost:3000
API | http://localhost:8000
API Docs (Swagger) | http://localhost:8000/docs
Ollama | http://localhost:11434

---

## Configuration
All configuration is via the `.env` file. Key toggles:

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
```

### Frontend

```bash
cd frontend

npm install

# Dev server (hot reload)
npm run dev

# Lint
npm run lint
```
---
