"""Canary - AI-powered sentiment analysis and tracking."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.topics import router as topics_router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    # Startup
    # Database engine is created on import; nothing extra needed yet.
    # In the future, this is where we'd initialize connection pools,
    # start background workers, etc.
    yield
    # Shutdown
    from app.core.database import engine

    await engine.dispose()


app = FastAPI(
    title="Canary",
    description="AI-powered sentiment analysis and tracking",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS - permissive for local dev, lock down in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(topics_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
