"""Database connection and session management."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from src.core.config import settings

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.python_env == "development",
    pool_pre_ping=True,
    pool_recycle=3600,
)


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for getting database session.
    
    Yields:
        Session: Database session
    """
    with Session(engine) as session:
        yield session


# Type alias for session dependency
SessionDep = Annotated[Session, Depends(get_session)]
