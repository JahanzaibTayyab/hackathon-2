# Todo Hackathon Constitution

## Core Principles

### I. Test-First Development (NON-NEGOTIABLE)

TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced. All features must have tests before implementation.

### II. CLI Interface

Every feature exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support both human-readable and structured formats.

### III. Simplicity First

Start simple, YAGNI principles. No over-engineering. Add complexity only when proven necessary. Phase 1 uses only Python standard library.

### IV. Spec-Driven Development

Follow Spec-Kit Plus workflow: Constitution → Specify → Plan → Tasks → Implement. All features must go through the full spec-driven process.

### V. Code Quality

- Clean, readable, well-documented code
- Type hints where appropriate (Python 3.11+)
- Follow PEP 8 style guidelines
- Meaningful variable and function names

### VI. Incremental Delivery

Each phase delivers independently testable, working software. MVP first, then enhancements.

## Technology Standards

### Phase 1 Requirements

- **Language**: Python 3.11+
- **Dependencies**: Standard library only (no external packages)
- **Testing**: pytest
- **Storage**: In-memory (dictionaries/lists)
- **Interface**: Console/CLI only

### Code Standards

- Type hints for function signatures
- Docstrings for public functions/classes
- Error handling with clear messages
- No hardcoded values (use constants)

## Development Workflow

### Spec-Kit Plus Workflow

1. **Constitution**: Define principles (this document)
2. **Specify**: Create feature specification (`/sp.specify`)
3. **Plan**: Create implementation plan (`/sp.plan`)
4. **Tasks**: Break down into testable tasks (`/sp.tasks`)
5. **Implement**: Follow TDD (Red-Green-Refactor)

### Testing Requirements

- Minimum 80% code coverage
- Unit tests for all models and services
- Integration tests for user workflows
- Tests must pass before merging

### Quality Gates

- All tests pass
- Code coverage ≥ 80%
- No linter errors
- Spec-driven artifacts complete

## Governance

Constitution supersedes all other practices. Amendments require documentation, approval, and migration plan.

All PRs/reviews must verify compliance. Complexity must be justified. Use this constitution for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2025-01-27 | **Last Amended**: 2025-01-27
