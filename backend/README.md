# TransKeep Backend

FastAPI + Python 3.11 backend for the TransKeep document translation platform.

## 🎯 Quick Start

### Using uv (Recommended)

```bash
# Create virtual environment
uv venv

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install -e .

# Run development server
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API docs.

### Using Docker

```bash
docker build -t transkeep-backend .
docker run -p 8000:8000 transkeep-backend
```

## 📦 Dependencies

### Core
- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM
- **Alembic**: Database migrations

### Database & Cache
- **PostgreSQL**: Primary database
- **Redis**: Session caching & job queue
- **Celery**: Async task processing

### APIs & Services
- **DeepL**: Translation API
- **Anthropic (Claude)**: Tone customization
- **google-auth**: OAuth 2.0
- **boto3**: AWS S3 integration

### Observability
- **OpenTelemetry**: Distributed tracing
- **Jaeger**: Trace visualization

### Development
- **pytest**: Testing framework
- **black**: Code formatting
- **ruff**: Linting
- **mypy**: Type checking

## 📁 Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI app setup & routes
├── config.py            # Settings & environment variables
├── dependencies.py      # Auth, DB session injection
├── routers/             # API route modules
│   ├── auth.py              # /login/google, /logout
│   ├── upload.py            # /upload (file chunks)
│   ├── translation.py       # /status, /download
│   └── user.py              # /me, /settings
├── models/              # SQLAlchemy models
│   ├── user.py              # User model
│   ├── translation.py       # Translation job model
│   └── document.py          # Document block model
├── schemas/             # Pydantic request/response models
│   ├── auth.py
│   ├── upload.py
│   └── translation.py
├── services/            # Business logic
│   ├── auth_service.py      # OAuth handling
│   ├── pdf_service.py       # PDF extraction & reconstruction
│   ├── translation_service.py # Translation orchestration
│   ├── tone_service.py      # Tone customization
│   └── s3_service.py        # S3 file storage
├── celery_app.py        # Celery configuration
├── tasks/               # Celery tasks
│   ├── extract_and_translate.py
│   ├── apply_tone.py
│   └── cleanup.py
└── utils/               # Utilities
    ├── logger.py            # Logging setup
    └── errors.py            # Custom exceptions
```

## 🛠 Available Commands

### Development

```bash
# Run dev server with reload
uvicorn app.main:app --reload

# Run Celery worker
celery -A app.celery_app worker -l info

# Run Celery beat (scheduler)
celery -A app.celery_app beat -l info
```

### Database

```bash
# Create migrations
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing & Quality

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Linting
ruff check app/

# Code formatting
black app/

# Type checking
mypy app/

# Format in-place
black app/
ruff check app/ --fix
```

## 🔐 Authentication

Google OAuth via `google-auth`:

```python
# Verify OAuth token
from app.services.auth_service import verify_google_token

user_info = verify_google_token(token)
```

JWT tokens for subsequent API calls:

```python
# Create JWT token
from app.services.auth_service import create_access_token

token = create_access_token(user_id)
```

## 📡 API Endpoints

### Authentication
- `POST /auth/login/google` - Login with Google token
- `POST /auth/logout` - Logout and revoke token

### Document Upload
- `POST /api/v1/upload` - Upload PDF (chunked)
- `GET /api/v1/status/{job_id}` - Check translation status

### Translation Management
- `GET /api/v1/translations` - List user's translations
- `GET /api/v1/download/{job_id}` - Download translated PDF

### User Management
- `GET /api/v1/me` - Current user profile
- `PATCH /api/v1/settings` - Update user settings

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  google_id VARCHAR UNIQUE,
  email VARCHAR UNIQUE,
  name VARCHAR,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Translations Table
```sql
CREATE TABLE translations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  original_file_path VARCHAR,
  translated_file_path VARCHAR,
  status VARCHAR,  -- pending, processing, completed, failed
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Document Blocks Table
```sql
CREATE TABLE document_blocks (
  id UUID PRIMARY KEY,
  translation_id UUID REFERENCES translations(id),
  page_number INT,
  block_number INT,
  original_text TEXT,
  translated_text TEXT,
  coordinates JSONB
);
```

## 🔄 Translation Pipeline

1. **Upload**: User uploads PDF → Store in S3
2. **Extract**: PyMuPDF extracts text blocks with coordinates
3. **Queue**: Celery task enqueued for processing
4. **Translate**: Batch translation via DeepL API
5. **Tone**: Optional Claude API call for tone adjustment
6. **Reconstruct**: PDF rebuilt with translated text
7. **Store**: Result saved to S3, DB updated
8. **Download**: User downloads via pre-signed URL

## 🚀 Deployment

### Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
JWT_SECRET=your_secret_key
GOOGLE_CLIENT_ID=your_client_id
DEEPL_API_KEY=your_api_key
CLAUDE_API_KEY=your_api_key
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml requirements.txt .
RUN pip install uv && uv pip install -r requirements.txt
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

### AWS ECS

```bash
# Push image to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <ECR_URI>
docker tag transkeep-backend:latest <ECR_URI>/transkeep-backend:latest
docker push <ECR_URI>/transkeep-backend:latest

# Deploy via CloudFormation/Terraform
```

## 📚 Resources

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [Celery Docs](https://docs.celeryproject.io)
- [Alembic Docs](https://alembic.sqlalchemy.org)

## 🐛 Troubleshooting

### Dependency Install Issues
```bash
# Clear cache and reinstall
uv pip sync --refresh  # or uv pip install -e . --force-reinstall
```

### Database Connection Error
```bash
# Test connection
python -c "from sqlalchemy import create_engine; create_engine(os.getenv('DATABASE_URL')).connect()"
```

### Celery Tasks Not Running
```bash
# Restart worker
celery -A app.celery_app worker -l debug

# Check Redis connection
redis-cli ping
```

### JWT Token Expired
Tokens expire after 24 hours. Client must re-authenticate via Google OAuth.

---

**Part of TransKeep MVP** | Last Updated: 2025-11-14

