# Implementation Plan: Phase 1 - In-Memory Python Console App

**Branch**: `phase-1-in-memory-console` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Hackathon II - Todo Spec-Driven Development requirements for Phase 1

## Summary

Phase 1 delivers a fully functional in-memory Todo application as a Python console application. This is the foundation phase that implements basic Todo CRUD operations without any persistence layer. The application will run in the terminal and allow users to manage todos through a command-line interface.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: None (standard library only for Phase 1)  
**Storage**: In-memory (Python dictionaries/lists)  
**Testing**: pytest  
**Target Platform**: Cross-platform (Linux, macOS, Windows)  
**Project Type**: Single Python package  
**Performance Goals**: Handle 1000+ todos in memory without noticeable lag  
**Constraints**: No external dependencies, no database, console-only interface  
**Scale/Scope**: Single-user, in-memory, session-based (data lost on exit)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Test-First Development: All features must have tests written first
- ✅ CLI Interface: Console-based interface with clear commands
- ✅ Simplicity: Start simple, no over-engineering
- ✅ Code Quality: Clean, readable, well-documented code

## Project Structure

### Documentation (this feature)

```text
specs/phase-1-in-memory-console/
├── plan.md              # This file
├── spec.md              # Feature requirements (to be created)
├── tasks.md             # Implementation tasks (to be created)
└── quickstart.md        # User guide (to be created)
```

### Code Structure

```text
todo_hackathon/
├── pyproject.toml       # Project configuration
├── README.md            # Project documentation
├── src/
│   └── todo_hackathon/
│       ├── __init__.py
│       ├── main.py      # Entry point (CLI)
│       ├── models.py    # Todo data models
│       ├── storage.py   # In-memory storage implementation
│       └── commands.py   # Command handlers
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_storage.py
    ├── test_commands.py
    └── test_integration.py
```

## Architecture Overview

### Core Components

1. **Todo Model** (`models.py`)
   - Simple data class/dataclass for Todo items
   - Fields: id, title, description (optional), completed (bool), created_at, updated_at

2. **In-Memory Storage** (`storage.py`)
   - Dictionary-based storage (id -> Todo)
   - CRUD operations: create, read, update, delete, list
   - No persistence - data exists only in memory

3. **Command Interface** (`commands.py`)
   - Parse user input
   - Route to appropriate handlers
   - Format output for display

4. **CLI Entry Point** (`main.py`)
   - Interactive loop or command-line arguments
   - Handle user input/output
   - Error handling and user feedback

### Data Flow

```
User Input → CLI Parser → Command Handler → Storage → Todo Model
                ↓
         Formatted Output → User
```

## Feature Requirements (High-Level)

### Must Have (MVP)

1. **Create Todo**
   - Add new todo with title
   - Optional description
   - Auto-generate ID
   - Set created_at timestamp

2. **List Todos**
   - Show all todos
   - Display: ID, title, status (completed/incomplete)
   - Optional: filter by status

3. **Update Todo**
   - Mark todo as completed/incomplete
   - Update title/description
   - Update updated_at timestamp

4. **Delete Todo**
   - Remove todo by ID
   - Confirm deletion (optional)

5. **View Todo**
   - Show single todo details
   - Display all fields

### Nice to Have (Phase 1 Bonus)

- Filter todos by status
- Search todos by title
- Sort todos (by date, status)
- Clear all completed todos
- Statistics (total, completed, pending)

## Implementation Phases

### Phase 1: Setup
- Project structure
- Testing framework setup
- Basic imports and dependencies

### Phase 2: Core Models
- Todo model/dataclass
- Validation logic
- Timestamp handling

### Phase 3: Storage Layer
- In-memory storage implementation
- CRUD operations
- Error handling

### Phase 4: Command Layer
- Command parsing
- Command handlers
- Input validation

### Phase 5: CLI Interface
- Interactive loop
- User input/output
- Error messages

### Phase 6: Integration & Polish
- End-to-end testing
- Error handling improvements
- User experience enhancements

## Testing Strategy

### Unit Tests
- Model validation
- Storage operations (CRUD)
- Command parsing

### Integration Tests
- Full user workflows
- Error scenarios
- Edge cases

### Test Coverage Goal
- Minimum 80% code coverage
- All critical paths tested

## Error Handling

- Invalid commands → Clear error message
- Invalid todo ID → "Todo not found" message
- Missing required fields → Validation error
- Empty state → Friendly message

## User Experience

### Command Examples
```
> add "Buy groceries" "Milk, eggs, bread"
Todo created: #1 - Buy groceries

> list
1. [ ] Buy groceries (Milk, eggs, bread)
2. [x] Complete project

> complete 1
Todo #1 marked as completed

> delete 2
Todo #2 deleted
```

### Output Format
- Clear, readable format
- Consistent styling
- Helpful error messages
- Success confirmations

## Dependencies

**Phase 1**: None (standard library only)
- `dataclasses` (Python 3.7+)
- `datetime`
- `typing`

**Future Phases**: Will add dependencies as needed

## Risks and Mitigation

1. **Risk**: Unclear command syntax
   - **Mitigation**: Clear documentation, help command, examples

2. **Risk**: Poor error messages
   - **Mitigation**: User testing, clear error messages

3. **Risk**: Memory issues with large todo lists
   - **Mitigation**: Phase 1 scope is reasonable (1000+ todos should be fine)

## Success Criteria

- ✅ All CRUD operations work correctly
- ✅ Tests pass with 80%+ coverage
- ✅ User can complete basic workflows
- ✅ Code is clean and maintainable
- ✅ No external dependencies
- ✅ Works on all major platforms

## Next Steps

1. Create detailed specification (spec.md)
2. Break down into tasks (tasks.md)
3. Set up test framework
4. Implement following TDD approach

