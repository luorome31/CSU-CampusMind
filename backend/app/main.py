"""
CampusMind Backend Application
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.database.session import create_db_and_tables
from app.config import settings

# Configure loguru for uvicorn - output to stdout
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
        }
    ]
)

from app.api.v1 import crawl, index, knowledge, knowledge_file, retrieve, completion, auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup and shutdown logic."""
    logger.info("Initializing database tables...")
    try:
        create_db_and_tables()
        logger.info(f"Database initialized: {settings.database_url}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CampusMind API",
        description="CampusMind - AI-powered campus assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    # NOTE: CORS misconfiguration - allow_origins=["*"] with allow_credentials=True is rejected by browsers
    # This is a pre-existing issue to be addressed separately
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(crawl.router, prefix="/api/v1")
    app.include_router(index.router, prefix="/api/v1")
    app.include_router(knowledge.router, prefix="/api/v1")
    app.include_router(knowledge_file.router, prefix="/api/v1")
    app.include_router(retrieve.router, prefix="/api/v1")
    app.include_router(completion.router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
