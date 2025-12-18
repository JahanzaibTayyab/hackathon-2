# Quickstart Guide: Phase 1 - In-Memory Python Console Todo App

**Date**: 2025-01-27  
**Feature**: Phase 1 Console Todo App

## Installation

1. Ensure Python 3.11+ is installed:
   ```bash
   python --version  # Should show 3.11 or higher
   ```

2. Install project dependencies (pytest for testing):
   ```bash
   cd todo_hackathon
   pip install -e ".[dev]"  # If dev dependencies are configured
   # OR
   pip install pytest  # For testing only
   ```

3. Run the application:
   ```bash
   python -m todo_hackathon
   # OR
   todo-hackathon  # If entry point is configured
   ```

## Basic Usage

### Starting the Application

The application starts in interactive mode. You'll see a prompt:
```
> 
```

### Creating a Todo

```
> add "Buy groceries"
Todo created: #1 - Buy groceries

> add "Complete project" "Finish the todo app implementation"
Todo created: #2 - Complete project
```

### Listing Todos

```
> list
1. [ ] Buy groceries
2. [ ] Complete project (Finish the todo app implementation)
```

### Viewing a Single Todo

```
> view 1
Todo #1
Title: Buy groceries
Description: 
Status: Incomplete
Created: 2025-01-27 10:30:00
Updated: 2025-01-27 10:30:00
```

### Marking Todo as Completed

```
> complete 1
Todo #1 marked as completed

> list
1. [x] Buy groceries
2. [ ] Complete project (Finish the todo app implementation)
```

### Marking Todo as Incomplete

```
> incomplete 1
Todo #1 marked as incomplete
```

### Updating a Todo

```
> update 1 title "Buy groceries and cook dinner"
Todo #1 updated

> update 1 description "Milk, eggs, bread, chicken"
Todo #1 updated
```

### Deleting a Todo

```
> delete 1
Todo #1 deleted

> list
1. [ ] Complete project (Finish the todo app implementation)
```

### Getting Help

```
> help
Available commands:
  add <title> [description]  - Create a new todo
  list                       - List all todos
  view <id>                  - View a single todo
  complete <id>              - Mark todo as completed
  incomplete <id>            - Mark todo as incomplete
  update <id> <field> <value> - Update todo field (title/description)
  delete <id>                 - Delete a todo
  help                       - Show this help message
  exit                       - Exit the application
```

### Exiting the Application

```
> exit
Goodbye!
```

## Error Scenarios

### Todo Not Found

```
> view 999
Error: Todo #999 not found
```

### Empty Title

```
> add ""
Error: Todo title cannot be empty
```

### Invalid Command

```
> invalid-command
Error: Unknown command 'invalid-command'. Type 'help' for available commands.
```

### Empty Todo List

```
> list
No todos yet. Create one with 'add <title>'
```

## Testing

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=todo_hackathon --cov-report=html
```

## Example Workflow

```
> add "Learn Python"
Todo created: #1 - Learn Python

> add "Build todo app" "Console-based todo application"
Todo created: #2 - Build todo app

> list
1. [ ] Learn Python
2. [ ] Build todo app (Console-based todo application)

> complete 1
Todo #1 marked as completed

> update 2 description "Console-based todo application with full CRUD"
Todo #2 updated

> view 2
Todo #2
Title: Build todo app
Description: Console-based todo application with full CRUD
Status: Incomplete
Created: 2025-01-27 10:35:00
Updated: 2025-01-27 10:36:00

> delete 1
Todo #1 deleted

> list
1. [ ] Build todo app (Console-based todo application with full CRUD)

> exit
Goodbye!
```

