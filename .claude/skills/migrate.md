# Database Migration Skill

Run database migrations to create or update database tables.

## Usage
```bash
/migrate
```

## What it does
1. Runs the database migration script to create/update tables
2. Creates: tasks, conversations, and messages tables
3. Verifies migration completed successfully

## Commands
```bash
cd backend && uv run python scripts/create_tables.py
```

## Success Criteria
- Script completes without errors
- Tables are created successfully
- Output shows "✅ Database tables created successfully!"
