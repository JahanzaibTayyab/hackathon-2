# Todo Hackathon - Phase 1

In-memory Python console todo application. This is Phase 1 of the Hackathon II - Todo Spec-Driven Development project.

## Features

- ✅ Create todos with title and optional description
- ✅ List all todos
- ✅ View single todo details
- ✅ Mark todos as completed/incomplete
- ✅ Update todo title and description
- ✅ Delete todos
- ✅ Interactive CLI interface

## Installation

1. Ensure Python 3.11+ is installed:

   ```bash
   python --version
   ```

2. Install the package and dependencies using `uv`:

   ```bash
   cd todo_hackathon
   uv sync --dev
   ```

   This will:

   - Create a virtual environment (`.venv`)
   - Install the package in editable mode
   - Install all development dependencies (pytest, pytest-cov)

3. Activate the virtual environment (optional - you can use `uv run` instead):

   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

## Usage

### Running the Application

Using `uv` (recommended):

```bash
uv run python -m todo_hackathon
# OR
uv run todo-hackathon
```

Or if virtual environment is activated:

```bash
python -m todo_hackathon
# OR
todo-hackathon
```

### Available Commands

- `add <title> [description]` - Create a new todo
- `list` - List all todos
- `view <id>` - View a single todo
- `complete <id>` - Mark todo as completed
- `incomplete <id>` - Mark todo as incomplete
- `update <id> <field> <value>` - Update todo field (title/description)
- `delete <id>` - Delete a todo
- `help` - Show help message
- `exit` - Exit the application

### Example Session

```
> add "Buy groceries" "Milk, eggs, bread"
Todo created: #1 - Buy groceries

> add "Complete project"
Todo created: #2 - Complete project

> list
1. [ ] Buy groceries (Milk, eggs, bread)
2. [ ] Complete project

> complete 1
Todo #1 marked as completed

> view 1
Todo #1
Title: Buy groceries
Description: Milk, eggs, bread
Status: Completed
Created: 2025-01-27 10:30:00
Updated: 2025-01-27 10:35:00

> delete 2
Todo #2 deleted

> exit
Goodbye!
```

## Testing

Run the test suite using `uv`:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=todo_hackathon --cov-report=html
```

## Project Structure

```
todo_hackathon/
├── src/
│   └── todo_hackathon/
│       ├── __init__.py
│       ├── main.py          # Entry point
│       ├── models.py         # Todo model
│       ├── storage.py        # In-memory storage
│       ├── commands.py       # Command handlers
│       ├── cli.py            # CLI parser
│       └── exceptions.py     # Custom exceptions
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
└── pyproject.toml
```

## Development

This project follows Spec-Driven Development (SDD) using Spec-Kit Plus:

1. **Constitution** - Project principles and standards
2. **Specification** - Feature requirements and user stories
3. **Plan** - Technical design and architecture
4. **Tasks** - Implementation breakdown
5. **Implementation** - TDD (Test-Driven Development)

See `/specs/phase-1-in-memory-console/` for all spec-driven artifacts.

## Phase 1 Scope

- ✅ In-memory storage (no persistence)
- ✅ Console/CLI interface only
- ✅ Python standard library only (no external dependencies)
- ✅ Basic CRUD operations
- ✅ Single-user application

## License

Part of Hackathon II - Todo Spec-Driven Development
