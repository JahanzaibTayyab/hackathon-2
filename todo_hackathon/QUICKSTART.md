# Quick Start Guide

## Installation

1. **Install dependencies using uv:**
   ```bash
   uv sync --extra dev
   ```
   
   Or if you prefer the uv-specific dev dependencies:
   ```bash
   uv sync --dev
   ```

2. **If dev dependencies still don't install, try:**
   ```bash
   uv pip install pytest pytest-cov
   ```

## Running the Application

**Option 1: Using uv run (recommended)**
```bash
uv run python -m todo_hackathon
```

**Option 2: Using the entry point script**
```bash
uv run todo-hackathon
```

**Option 3: Activate venv and run directly**
```bash
source .venv/bin/activate  # On macOS/Linux
python -m todo_hackathon
```

## Running Tests

```bash
# Using uv
uv run pytest

# Or if venv is activated
pytest
```

## Troubleshooting

### Issue: `pytest` not found
**Solution:** Make sure dev dependencies are installed:
```bash
uv sync --extra dev
# OR
uv pip install pytest pytest-cov
```

### Issue: `No module named todo_hackathon.__main__`
**Solution:** This should be fixed with the `__main__.py` file. Make sure you're in the `todo_hackathon` directory and the package is installed:
```bash
uv sync
```

### Issue: Module not found errors
**Solution:** Ensure the package is installed in editable mode:
```bash
uv sync
```

