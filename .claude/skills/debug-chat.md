# Debug Chat Issues Skill

Debug issues with the AI chat functionality.

## Usage
```bash
/debug-chat
```

## What it does
1. Checks backend server status
2. Verifies OpenAI API key is loaded
3. Reviews recent chat errors in logs
4. Tests database connectivity for conversations/messages
5. Provides troubleshooting suggestions

## Commands
```bash
echo "=== Chat Debug Report ==="

# 1. Backend Status
echo -e "\n1. Backend Server Status:"
curl -s http://localhost:8000/health 2>&1 | grep -q "healthy" && echo "✓ Backend is healthy" || echo "✗ Backend not responding"

# 2. OpenAI Configuration
echo -e "\n2. OpenAI Configuration:"
cd backend
if grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "✓ OpenAI API key is set"
else
    echo "✗ OpenAI API key missing or invalid"
    echo "  Fix: Add OPENAI_API_KEY=sk-xxx to backend/.env"
fi

# 3. Recent Errors
echo -e "\n3. Recent Chat Errors:"
tail -100 /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b0cdd87.output | grep -i "error\|exception\|traceback" | tail -10

# 4. Database Tables
echo -e "\n4. Database Tables Check:"
cd backend && uv run python -c "
from src.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print('✓ conversations' if 'conversations' in tables else '✗ conversations missing')
print('✓ messages' if 'messages' in tables else '✗ messages missing')
" 2>&1

# 5. Recent Chat Activity
echo -e "\n5. Last 5 Chat Requests:"
tail -200 /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b0cdd87.output | grep "POST /api/v1/chat" | tail -5

echo -e "\n=== Troubleshooting Tips ==="
echo "• If OpenAI key is missing: Add it to backend/.env and restart backend"
echo "• If tables are missing: Run /migrate skill"
echo "• If no response: Check browser console (F12) for frontend errors"
echo "• If 401 error: Token authentication issue, try logging in again"
```

## Success Criteria
- Identifies specific issues with chat functionality
- Provides actionable troubleshooting steps
- Shows recent error messages if any
