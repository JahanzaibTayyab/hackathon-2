# Test AI Agent Skill

Test the AI agent with various sample prompts.

## Usage
```bash
/test-agent
```

## What it does
1. Verifies agent is configured correctly
2. Tests each tool with sample prompts
3. Validates responses
4. Reports any tool failures

## Test Cases

### 1. Add Task Tool
- Prompt: "Add a task to buy milk"
- Expected: Task created with title "Buy milk"

### 2. List Tasks Tool
- Prompt: "Show me all my tasks"
- Expected: Returns list of tasks

### 3. Complete Task Tool
- Prompt: "Mark task 1 as complete"
- Expected: Task 1 status updated to completed

### 4. Update Task Tool
- Prompt: "Change task 2 title to 'Call doctor'"
- Expected: Task 2 title updated

### 5. Delete Task Tool
- Prompt: "Delete task 3"
- Expected: Task 3 removed from database

## Commands
```bash
echo "=== AI Agent Test Suite ==="

# Check agent configuration
echo -e "\n1. Checking Agent Configuration:"
cd backend && uv run python -c "
from src.agent.agent import create_chat_agent
try:
    agent = create_chat_agent('test_user')
    print(f'✓ Agent created: {agent.name}')
    print(f'✓ Tools available: {len(agent.tools)}')
    for tool in agent.tools:
        print(f'  - {tool.name if hasattr(tool, \"name\") else \"unknown\"}')
except Exception as e:
    print(f'✗ Agent configuration error: {e}')
"

# Check OpenAI connection
echo -e "\n2. Checking OpenAI Configuration:"
grep -q "OPENAI_API_KEY=sk-" backend/.env && echo "✓ OpenAI API key configured" || echo "✗ OpenAI API key missing"

# Manual test instructions
echo -e "\n3. Manual Test Instructions:"
echo "Open http://localhost:3000/chat and test these prompts:"
echo "  1. 'Add a task to buy groceries'"
echo "  2. 'Show me all my tasks'"
echo "  3. 'Mark task 1 as complete'"
echo "  4. 'Delete task 2'"
echo ""
echo "Watch backend logs for tool calls:"
tail -f /tmp/claude/-Users-zaib-Panaverse-hackathon-2/tasks/b0cdd87.output | grep -E "tool|function"
```

## Success Criteria
- Agent is properly configured
- All 5 tools are available
- OpenAI API key is valid
- Tools execute without errors
- Agent provides helpful responses
