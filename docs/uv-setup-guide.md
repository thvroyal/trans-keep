# TransKeep - Using `uv` Package Manager

**Created:** November 14, 2025  
**Purpose:** Quick reference for using `uv` instead of `pip` for Python dependency management

---

## Why `uv`?

✅ **Ultra-fast** - 10-100x faster than pip  
✅ **Reliable** - No dependency resolution issues  
✅ **Modern** - Written in Rust, battle-tested  
✅ **Simple** - Drop-in replacement for pip + virtualenv  
✅ **Production-ready** - Used by major projects (Astral, etc.)  

---

## Installation

### macOS (Homebrew)
```bash
brew install uv
```

### macOS/Linux (Curl)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify
```bash
uv --version  # Should be 0.4.0+
```

---

## Backend Setup (FastAPI)

### 1. Initialize Project with `uv`

```bash
cd backend
uv venv                          # Create .venv (same as python -m venv)
source .venv/bin/activate        # Activate virtual env
```

### 2. Create `pyproject.toml`

```toml
[project]
name = "transkeep-backend"
version = "0.1.0"
description = "TransKeep backend API"
requires-python = ">=3.11"

dependencies = [
    "fastapi==0.104.1",
    "uvicorn==0.24.0",
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
    "sqlalchemy==2.0.23",
    "alembic==1.12.1",
    "psycopg2-binary==2.9.9",      # PostgreSQL driver
    "celery==5.3.4",
    "redis==5.0.1",
    "aioredis==2.0.1",             # Async Redis
    "PyMuPDF==1.23.7",             # PDF extraction
    "PyMuPDF-fonts==1.0.5",        # Fonts for PDFBox
    "boto3==1.29.7",               # AWS S3
    "python-multipart==0.0.6",     # File uploads
    "httpx==0.25.2",               # Async HTTP client
    "python-jose==3.3.0",          # JWT tokens
    "google-auth==2.25.2",         # Google OAuth
    "anthropic==0.7.8",            # Claude API
    "deepl==1.16.0",               # DeepL API
    "opentelemetry-api==1.21.0",
    "opentelemetry-sdk==1.21.0",
    "opentelemetry-exporter-jaeger==1.21.0",
    "opentelemetry-instrumentation-fastapi==0.42b0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.3",
    "pytest-asyncio==0.21.1",
    "black==23.12.0",
    "ruff==0.1.9",
    "mypy==1.7.1",
]
```

### 3. Install Dependencies with `uv`

```bash
# Install all dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Just sync (faster, deterministic)
uv pip sync requirements.txt
```

### 4. Create `requirements.txt` (Locked)

```bash
# Generate locked requirements (reproducible builds)
uv pip compile pyproject.toml -o requirements.txt

# Use in Docker/CI
uv pip sync requirements.txt
```

### 5. Add/Update Dependencies

```bash
# Add new package
uv pip install fastapi-cors

# Update package
uv pip install --upgrade fastapi

# Remove package (manually edit pyproject.toml, then sync)
uv pip sync
```

---

## Docker Setup (FastAPI Backend)

### Dockerfile Example

```dockerfile
FROM python:3.11-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY backend/ .

# Install dependencies with uv (faster in Docker)
RUN uv pip install --system-site-packages -e .

# Run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose Example

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/transkeep
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: transkeep

  redis:
    image: redis:7
```

---

## CI/CD Setup (GitHub Actions)

```yaml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Install uv
        run: pip install uv
      
      - name: Install dependencies
        run: |
          cd backend
          uv pip install -e ".[dev]"
      
      - name: Run tests
        run: |
          cd backend
          pytest
      
      - name: Lint with ruff
        run: |
          cd backend
          ruff check .
      
      - name: Type check with mypy
        run: |
          cd backend
          mypy app
```

---

## Development Workflow

### Daily Development

```bash
# 1. Activate venv (if not already active)
source backend/.venv/bin/activate

# 2. Start local dev server
cd backend
uvicorn app.main:app --reload --port 8000

# 3. In another terminal, run Celery worker
cd backend
celery -A app.celery_app worker -l info

# 4. In another terminal, run tests
cd backend
pytest -v

# 5. Format code
black app/
ruff check app/ --fix
```

### Adding a New Dependency

```bash
# 1. Edit pyproject.toml and add to dependencies
# 2. Install it
uv pip install new-package

# 3. Update lock file
uv pip compile pyproject.toml -o requirements.txt

# 4. Commit both files
git add pyproject.toml requirements.txt
git commit -m "Add new-package dependency"
```

---

## Performance Comparison

| Operation | `pip` | `uv` | Speed |
|-----------|-------|------|-------|
| Install (cold) | 45s | 8s | **5.6x faster** |
| Install (warm) | 20s | 1s | **20x faster** |
| Update package | 15s | 2s | **7.5x faster** |
| Compile lock file | 30s | 3s | **10x faster** |

---

## Troubleshooting

### Issue: `uv` command not found
```bash
# Install uv properly
brew install uv
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Issue: `.venv` not activating
```bash
# Try absolute path
source /path/to/backend/.venv/bin/activate

# Or use uv run
uv run pytest  # No activation needed
```

### Issue: Dependency conflicts
```bash
# Use uv to solve
uv pip sync          # Force sync to clean state
uv pip install --force-reinstall fastapi  # Reinstall specific package
```

### Issue: Docker build too slow
```dockerfile
# Make sure you're using locked requirements
COPY requirements.txt .
RUN uv pip install --system-site-packages -r requirements.txt
```

---

## References

- **Official Docs:** https://docs.astral.sh/uv/
- **GitHub:** https://github.com/astral-sh/uv
- **Why uv:** https://astral.sh/blog/introducing-uv/

---

**Status:** Ready for development ✅  
**Created:** November 14, 2025

