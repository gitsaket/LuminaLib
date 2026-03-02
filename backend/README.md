# Lumina Backend

FastAPI backend for LuminaLib library management system.

## Tech Stack

- FastAPI 0.111.0
- PostgreSQL with SQLAlchemy (async)
- Alembic for migrations
- JWT for authentication
- Factory LLM (Ollama/OpenAI) and Storage (Local/S3) backends. S3 is not implemented yet but the architecture supports it.

## Setup

Docker steps are in the main README. For local development, follow the steps below.

### Local Development

1. #Install Dependencies:

   ```bash
   cd backend
   python -m virtualenv ./venv
   source .venv/bin/activate  #bash , zsh
   source venv/bin/activate.fish # for fish shell
    .\venv\Scripts\Activate.ps1 # for Windows PowerShell
   soruce .\venv\Scripts\activate # for Windows cmd
   pip install -r requirements.txt
   ```

2. #Configure Environment:

   ```bash
   create .env file to add your environment variables (see .env.example for reference)
   otherwise core/config.py will use default values setup as BaseSettings by using Pydantic
   # Edit .env with your settings
   ```

3. #Run Migrations:

   ```bash
   alembic upgrade head
   ```

4. #Start Server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. #API
   # URL
   API will be available at `http://localhost:8000`
   # Docs
   API docs at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` (ReDoc).

## Configuration

```bash
# App
ENVIRONMENT: "development", "production"
LOG_LEVEL: "INFO"
ALLOWED_ORIGINS: "http://localhost:3000"

# Database
DATABASE_URL: "postgresql+asyncpg://lumina:luminasecret@db:5432/luminalib"

# Auth
SECRET_KEY: "1234567890abcdef"
ALGORITHM: "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: 60
REFRESH_TOKEN_EXPIRE_DAYS: 7

# Storage
STORAGE_BACKEND: "local"
LOCAL_STORAGE_PATH: "/tmp/luminalib_books"

# LLM
LLM_BACKEND: "ollama" / "openai"
OLLAMA_BASE_URL: "http://ollama:11434"
OLLAMA_MODEL: "llama3.2"
MAX_CONTENT_LENGTH: int = 2000
```

## Code Quality

```bash
ruff check .      # Check code
ruff format .     # Format code
ruff check --fix . # Auto-fix issues
pytest tests/    # Run tests
```

## Structure

## Project Structure

- `backend/`
  - `Dockerfile`
  - `requirements.txt`
  - `alembic/` — DB migrations
    - `env.py`
    - `versions/`
      - `0001_initial.py`
  - `db/`
    - `init.sql`
  - `app/`
    - `main.py` — FastAPI app factory
    - `core/`
      - `config.py` — Pydantic settings
      - `security.py` — JWT + bcrypt
      - `dependencies.py` — FastAPI DI
    - `api/v1/endpoints/`
      - `auth.py`
      - `books.py`
      - `recommendations.py`
    - `models/` — SQLAlchemy models
    - `schemas/` — Pydantic schemas
    - `repositories/` — DB query layer
    - `services/`
      - `storage/` — S3/local abstraction
      - `llm/` — Ollama/OpenAI abstraction
      - `recommendation_service.py`
    - `tasks/`
      - `backgroud.py` — Background tasks
    - `utils/`
      - `text_extraction.py`
