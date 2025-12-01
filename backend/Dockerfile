FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

WORKDIR /app

# Copy project files
COPY pyproject.toml requirements.txt* ./

# Install dependencies with uv (use system Python)
RUN uv pip install --system -r requirements.txt 2>/dev/null || uv pip install --system -e .

# Copy application code
COPY app/ ./app/

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

