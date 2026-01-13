# Run All Tests Skill

Run all tests for both frontend and backend.

## Usage
```bash
/test-all
```

## What it does
1. Runs backend unit and integration tests
2. Runs frontend Jest unit tests
3. Shows coverage reports
4. Reports any failures

## Commands
```bash
# Backend tests
cd backend && uv run pytest --cov

# Frontend tests
cd frontend && pnpm test --coverage
```

## Success Criteria
- All backend tests pass
- All frontend tests pass
- Coverage reports generated
- No test failures or errors
