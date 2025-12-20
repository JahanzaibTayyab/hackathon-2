"""FastAPI main application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import tasks
from src.core.config import settings
from src.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan event handler for startup and shutdown.
    
    Args:
        app: FastAPI application instance
    """
    # Startup: Database tables are created via migration script
    # create_db_and_tables()  # Commented out - tables created via scripts/create_tables.py
    yield
    # Shutdown: Cleanup (if needed)


app = FastAPI(
    title="Todo Backend API",
    description="Backend API for Todo application with user authentication",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Todo Backend API", "version": "1.0.0"}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
