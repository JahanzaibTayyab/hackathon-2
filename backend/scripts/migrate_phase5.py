"""Phase V Migration: Add advanced task features columns."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from src.core.database import engine


def migrate():
    """Add Phase V columns to tasks table."""
    print("Running Phase V Migration...")
    print("Adding advanced task features columns...")

    migrations = [
        # Add due_date column
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS due_date TIMESTAMP WITH TIME ZONE;
        """,
        # Add priority column with default
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium';
        """,
        # Add tags column as array
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';
        """,
        # Add recurrence_pattern as JSONB
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS recurrence_pattern JSONB;
        """,
        # Add next_occurrence for recurring tasks
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS next_occurrence TIMESTAMP WITH TIME ZONE;
        """,
        # Add reminder_sent flag
        """
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;
        """,
        # Create index on due_date for efficient queries
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_due_date
        ON tasks (due_date) WHERE due_date IS NOT NULL;
        """,
        # Create index on priority
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_priority
        ON tasks (priority);
        """,
        # Create GIN index on tags for array queries
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_tags
        ON tasks USING GIN (tags);
        """,
    ]

    with engine.connect() as conn:
        for i, migration in enumerate(migrations, 1):
            try:
                conn.execute(text(migration))
                conn.commit()
                print(f"  ✓ Migration {i}/{len(migrations)} completed")
            except Exception as e:
                print(f"  ! Migration {i}/{len(migrations)} skipped or failed: {e}")
                conn.rollback()

    print("\n✅ Phase V migration completed!")
    print("\nNew columns added:")
    print("  - due_date (TIMESTAMP WITH TIME ZONE)")
    print("  - priority (VARCHAR(10), default: 'medium')")
    print("  - tags (TEXT[])")
    print("  - recurrence_pattern (JSONB)")
    print("  - next_occurrence (TIMESTAMP WITH TIME ZONE)")
    print("  - reminder_sent (BOOLEAN, default: FALSE)")
    print("\nIndexes created:")
    print("  - idx_tasks_due_date")
    print("  - idx_tasks_priority")
    print("  - idx_tasks_tags (GIN)")


def rollback():
    """Rollback Phase V migration (remove columns)."""
    print("Rolling back Phase V Migration...")
    print("WARNING: This will remove all Phase V columns and their data!")

    rollback_sql = [
        "DROP INDEX IF EXISTS idx_tasks_due_date;",
        "DROP INDEX IF EXISTS idx_tasks_priority;",
        "DROP INDEX IF EXISTS idx_tasks_tags;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS due_date;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS priority;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS tags;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS recurrence_pattern;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS next_occurrence;",
        "ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent;",
    ]

    with engine.connect() as conn:
        for sql in rollback_sql:
            try:
                conn.execute(text(sql))
                conn.commit()
            except Exception as e:
                print(f"  ! Rollback step failed: {e}")
                conn.rollback()

    print("✅ Phase V rollback completed!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase V Database Migration")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (remove Phase V columns)",
    )
    args = parser.parse_args()

    if args.rollback:
        confirm = input("Are you sure you want to rollback? This will delete data! (yes/no): ")
        if confirm.lower() == "yes":
            rollback()
        else:
            print("Rollback cancelled.")
    else:
        migrate()
