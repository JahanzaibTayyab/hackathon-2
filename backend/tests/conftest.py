"""Pytest configuration and fixtures."""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.core.database import get_session
from src.models.task import Task


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="user_id")
def user_id_fixture():
    """Return a test user ID."""
    return "test-user-123"


@pytest.fixture(name="other_user_id")
def other_user_id_fixture():
    """Return another test user ID for isolation testing."""
    return "other-user-456"


@pytest.fixture(name="task_service")
def task_service_fixture(session: Session, user_id: str):
    """Create a TaskService instance."""
    from src.services.task_service import TaskService

    return TaskService(session, user_id)


@pytest.fixture(name="sample_task")
def sample_task_fixture(session: Session, user_id: str):
    """Create a sample task in the database."""
    task = Task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
        completed=False,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
