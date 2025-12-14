# 3. Backend Architecture

## 3.1 Backend Stack & Rationale

| Layer | Technology | Why |
|-------|------------|-----|
| **Framework** | FastAPI | Async-first, type-safe (Pydantic), auto-docs (Swagger) |
| **Runtime** | Python 3.11+ | Rich ecosystem (PyMuPDF, Celery, etc.) |
| **Package Manager** | uv | Ultra-fast, reliable Python package management |
| **Database** | PostgreSQL 15+ | Reliable, multi-tenant friendly, JSONB support |
| **Cache** | Redis 7+ | Session caching, job queue, real-time features |
| **Task Queue** | Celery 5+ | Distributed task processing for large PDFs |
| **Auth** | Google OAuth + JWT | Stateless, secure, integrates with FastAPI |
| **PDF Processing** | PyMuPDF + PDFBox | Fast extraction + layout-preserving reconstruction |
| **Translation API** | DeepL | Best-in-class quality |
| **Tone API** | Claude 3.5 Haiku | Lightweight, fast, tone-aware |
| **OCR** | LlamaParse | Fallback for scanned PDFs |

## 3.2 Backend Project Structure

```
backend/
├─ app/
│  ├─ main.py (FastAPI app setup)
│  ├─ config.py (settings, env vars)
│  ├─ dependencies.py (auth, db session)
│  ├─ routers/
│  │  ├─ auth.py (POST /login/google, /logout)
│  │  ├─ upload.py (POST /upload - chunked)
│  │  ├─ translation.py (GET /status, /download)
│  │  └─ user.py (GET /me, PATCH /settings)
│  ├─ models/
│  │  ├─ user.py (SQLAlchemy User model)
│  │  ├─ translation.py (SQLAlchemy Translation model)
│  │  ├─ schemas.py (Pydantic request/response schemas)
│  │  └─ database.py (DB connection + session factory)
│  ├─ services/
│  │  ├─ auth_service.py (Google OAuth, JWT validation)
│  │  ├─ upload_service.py (file handling, S3 upload)
│  │  ├─ translation_service.py (orchestration)
│  │  └─ freemium_service.py (usage tracking, limits)
│  ├─ workers/ (Celery tasks)
│  │  ├─ tasks.py (extract_translate, apply_tone, etc.)
│  │  └─ celery_app.py (Celery config)
│  └─ middleware/
│     ├─ auth_middleware.py (verify JWT)
│     ├─ tenant_middleware.py (extract tenant context)
│     └─ error_handler.py (global error handling)
├─ migrations/ (Alembic)
├─ tests/
│  ├─ test_api.py (endpoint tests)
│  ├─ test_services.py (business logic tests)
│  └─ test_workers.py (Celery task tests)
├─ requirements.txt (Python dependencies)
├─ Dockerfile (Container image)
├─ docker-compose.yml (Local dev: FastAPI + PostgreSQL + Redis)
├─ .env.example
└─ pyproject.toml (Poetry config)
```

## 3.3 API Endpoints (REST)

**Authentication:**
```
POST /api/v1/login/google
  Body: {token: "google_id_token"}
  Response: {access_token, user: {id, email, name}}

POST /api/v1/logout
  Response: {success: true}

GET /api/v1/me
  Headers: Authorization: Bearer {token}
  Response: {user: {id, email, subscription, usage}}
```

**Upload:**
```
POST /api/v1/upload
  Headers: Authorization: Bearer {token}
  Body: FormData { file: File, target_language: string }
  Response: {job_id, status: "queued"}
```

**Status & Download:**
```
GET /api/v1/status/{job_id}
  Headers: Authorization: Bearer {token}
  Response: {status, progress, page, eta_seconds}

GET /api/v1/download/{job_id}
  Headers: Authorization: Bearer {token}
  Response: Pre-signed S3 URL (client downloads directly from S3)
```

**User Settings:**
```
PATCH /api/v1/user/settings
  Body: {language_preference, theme}
  Response: {user: updated}
```

## 3.4 Database Schema

**users table:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL (multi-tenant isolation),
  google_id STRING UNIQUE NOT NULL,
  email STRING UNIQUE NOT NULL,
  name STRING,
  subscription_tier ENUM (free, pro, enterprise),
  usage_this_month INT DEFAULT 0,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

**translations table:**
```sql
CREATE TABLE translations (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL (foreign key to users.tenant_id),
  user_id UUID NOT NULL (foreign key to users.id),
  file_name STRING,
  file_size_mb INT,
  source_language STRING,
  target_language STRING,
  status ENUM (queued, processing, complete, error),
  progress_percent INT,
  original_file_path STRING (S3 path),
  result_file_path STRING (S3 path, null if processing),
  tone_applied STRING (original tone used),
  error_message TEXT (if status=error),
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  expires_at TIMESTAMP (delete after 24 hours)
);

CREATE INDEX idx_tenant_user ON translations(tenant_id, user_id);
CREATE INDEX idx_status ON translations(status);
```

**tenant_settings table (Phase 2):**
```sql
CREATE TABLE tenant_settings (
  id UUID PRIMARY KEY,
  tenant_id UUID UNIQUE NOT NULL,
  glossary_enabled BOOLEAN DEFAULT false,
  collaboration_enabled BOOLEAN DEFAULT false,
  created_at TIMESTAMP
);
```

---
