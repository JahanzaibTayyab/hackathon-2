"""Script to create database tables for tasks."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.core.database import engine
from src.models.task import Task
from src.core.database import SQLModel


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    
    # Create tasks table
    SQLModel.metadata.create_all(engine)
    
    print("✅ Tasks table created successfully!")
    print("\nNote: Better Auth tables (user, session, account, etc.) are managed by the frontend.")
    print("They will be created automatically when Better Auth first connects.")


if __name__ == "__main__":
    create_tables()
