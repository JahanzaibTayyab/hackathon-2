"""Script to create database tables."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import SQLModel, engine

# Import all models to register them with SQLModel
from src.models.conversation import Conversation  # noqa: F401
from src.models.message import Message  # noqa: F401
from src.models.task import Task  # noqa: F401


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    print("✅ Database tables created successfully!")
    print("   - tasks")
    print("   - conversations")
    print("   - messages")
    print("\nNote: Better Auth tables (user, session, account, etc.) are managed by the frontend.")
    print("They will be created automatically when Better Auth first connects.")


if __name__ == "__main__":
    create_tables()
