# Add AI Agent Tool Skill

Add a new tool/function to the AI agent for task management.

## Usage
```bash
/add-tool
```

## What it does
1. Guides you through creating a new tool
2. Adds the tool to the agent configuration
3. Updates the agent instructions
4. Provides example usage

## Interactive Prompts
The skill will ask you:
- Tool name (e.g., "search_tasks")
- Tool description (what it does)
- Parameters (name, type, description)
- Implementation logic

## Example Tool Structure
```python
@function_tool
def search_tasks(query: str) -> list[dict]:
    """
    Search tasks by keyword in title or description.

    Args:
        query: Search keyword

    Returns:
        List of matching tasks
    """
    with Session(engine) as session:
        task_service = TaskService(session=session, user_id=user_id)
        # Implementation here
        pass
```

## Steps to Add Manually
1. Open `backend/src/agent/agent.py`
2. Add new `@function_tool` decorated function inside `create_chat_agent()`
3. Add tool to the `tools` list in `Agent()` initialization
4. Update agent instructions to mention the new tool
5. Restart backend server

## Success Criteria
- New tool is defined with proper signature
- Tool is added to agent's tools list
- Agent can successfully call the new tool
- Instructions document the new capability
