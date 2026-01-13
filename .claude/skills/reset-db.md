# Reset Database Skill

Reset the database to a clean state (WARNING: Deletes all data).

## Usage
```bash
/reset-db
```

## What it does
1. Warns about data loss
2. Drops all tables (tasks, conversations, messages)
3. Recreates tables with fresh schema
4. Confirms reset completed

## Commands
```bash
echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
echo "This includes:"
echo "  - All tasks"
echo "  - All conversations"
echo "  - All messages"
echo ""
read -p "Are you sure? (type 'yes' to confirm): " confirm

if [ "$confirm" = "yes" ]; then
    echo "Resetting database..."

    # Drop and recreate tables
    cd backend && uv run python -c "
from src.core.database import SQLModel, engine
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message

print('Dropping all tables...')
SQLModel.metadata.drop_all(engine)
print('Creating fresh tables...')
SQLModel.metadata.create_all(engine)
print('✅ Database reset complete!')
"
else
    echo "Reset cancelled."
fi
```

## Success Criteria
- User confirms the action
- All tables are dropped
- Tables are recreated successfully
- Database is in clean state

## Notes
- Better Auth tables (user, session, account) are NOT affected
- Users will still be able to log in after reset
- Only task and chat data is deleted
