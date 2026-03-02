import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


def create_application() -> FastAPI:
    app = FastAPI(
        title="LuminaLib API",
        description="Library System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok", "environment": settings.ENVIRONMENT}

    return app


app = create_application()
