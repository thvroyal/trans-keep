# TransKeep - System Architecture Document

**Created:** November 14, 2025  
**Author:** Roy  
**Track:** Enterprise Method - Greenfield  
**Timeline:** 1-month MVP  

---

## Executive Summary

**Architecture Philosophy:** Simple, proven, scalable. Use battle-tested tech stacks with minimal custom code. Get to MVP fast, then optimize.

**Tech Stack:**
- **Frontend:** React 18 + TypeScript + Tailwind CSS v4 + ESLint + Prettier (Vite bundler)
- **Backend:** FastAPI + Python 3.11 + PostgreSQL + Redis + Celery
- **Infrastructure:** AWS (S3, ECS, RDS, ElastiCache, CloudFront)
- **External APIs:** DeepL (translation), Claude 3.5 Haiku (tone), LlamaParse (OCR), Google OAuth

**Key Architectural Decisions:**
1. ✅ Stateless backend for horizontal scaling
2. ✅ Async job processing for large PDFs (don't block user)
3. ✅ Multi-tenant from Day 1 (tenant isolation at data layer)
4. ✅ Progressive enhancement (MVP features only, Phase 2 ready)

---

## 1. System Overview

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                          │
│  React 18 App (React Router, TanStack Query, Zustand)       │
│  ├─ Upload Page                                              │
│  ├─ Review Page (Hero UI with PDF viewers)                  │
│  ├─ Tone & Edit Panels                                      │
│  └─ Auth (Google OAuth via NextAuth-like wrapper)           │
└─────────────────────────────────────────────────────────────┘
           ↓ (HTTPS)
┌─────────────────────────────────────────────────────────────┐
│                    API GATEWAY & CORS                        │
│  Public REST API (FastAPI)                                   │
│  ├─ Authentication endpoint                                  │
│  ├─ Document upload endpoint                                │
│  ├─ Translation status polling                              │
│  ├─ Download endpoint                                        │
│  └─ User settings endpoint                                   │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                           │
│  FastAPI Application (stateless, horizontally scalable)      │
│  ├─ Request validation (Pydantic)                            │
│  ├─ Authentication middleware (Google OAuth token verify)    │
│  ├─ Multi-tenant context extraction (from user_id)           │
│  ├─ Business logic (orchestration, not heavy lifting)        │
│  └─ Response formatting (JSON API)                           │
└─────────────────────────────────────────────────────────────┘
     ↙    ↓    ↘    ↙    ↓    ↘
┌──────────┐ ┌──────────┐ ┌──────────┐
│   JOB    │ │ DATABASE │ │  CACHE   │
│  QUEUE   │ │   LAYER  │ │  LAYER   │
│ (Celery) │ │PostgreSQL│ │  Redis   │
└──────────┘ └──────────┘ └──────────┘
     ↓
┌─────────────────────────────────────────────────────────────┐
│                 WORKER LAYER (Async Jobs)                   │
│  Celery Workers - Distributed Task Processing               │
│  ├─ PDF Extraction (PyMuPDF)                                 │
│  ├─ Translation (DeepL API calls)                            │
│  ├─ Tone Customization (Claude API calls)                    │
│  ├─ PDF Reconstruction (PDFBox)                              │
│  └─ Cleanup (delete temp files after 24h)                   │
└─────────────────────────────────────────────────────────────┘
     ↙    ↓    ↘    ↙    ↓    ↘
┌──────────┐ ┌──────────┐ ┌──────────┐
│   FILE   │ │ EXTERNAL │ │DATABASE  │
│ STORAGE  │ │   APIs   │ │ (Results)│
│ (AWS S3) │ │(DeepL)   │ │          │
│          │ │(Claude)  │ │PostgreSQL│
│          │ │(Google)  │ │          │
└──────────┘ └──────────┘ └──────────┘
     ↑            ↑             ↑
     └────────────┴─────────────┘
     Accessed by Workers & API
```

### 1.2 Request Flow: Upload to Download

```
1. USER UPLOADS FILE
   ├─ Drag-drop PDF to React component
   ├─ Frontend validates (file type, size)
   └─ Chunked upload to /api/v1/upload endpoint

2. SERVER RECEIVES CHUNKS
   ├─ FastAPI validates authentication (Google token)
   ├─ Extracts tenant_id from user context
   ├─ Stores chunks in S3 with tenant isolation
   ├─ Creates DB record: {user_id, job_id, file_path, status: pending}
   └─ Returns job_id to client

3. JOB QUEUED
   ├─ FastAPI queues Celery task: extract_and_translate
   ├─ Task includes: job_id, file_path, tenant_id
   └─ Client receives: {job_id, status: queued}

4. CLIENT POLLS STATUS
   ├─ Frontend polls /api/v1/status/{job_id} every 2 seconds
   └─ Response: {status: processing, progress: 25%, page: 12}

5. WORKER PROCESSES DOCUMENT
   ├─ Extract text + layout: PyMuPDF (5-10 sec for 500 pages)
   ├─ Translate in parallel: DeepL API (30-60 sec)
   ├─ Apply tone: Claude Haiku (20-40 sec)
   ├─ Reconstruct PDF: PDFBox (5-10 sec)
   ├─ Store result in S3: /translations/{tenant_id}/{job_id}/result.pdf
   ├─ Update DB: {status: complete, result_path: ..., created_at: now}
   └─ Celery marks task complete

6. CLIENT DETECTS COMPLETION
   ├─ Poll returns: {status: complete, result_path: ...}
   ├─ Frontend loads result PDF (from CloudFront CDN)
   ├─ Displays side-by-side review
   └─ Shows download button (prominent)

7. USER DOWNLOADS
   ├─ Clicks download button
   ├─ Frontend calls /api/v1/download/{job_id}
   ├─ FastAPI verifies ownership (tenant_id match)
   ├─ Returns pre-signed S3 URL
   └─ Browser downloads file directly from CloudFront
```

---

## 2. Frontend Architecture

### 2.1 Frontend Stack & Rationale

| Layer | Technology | Why |
|-------|------------|-----|
| **Framework** | React 18 + TypeScript | Industry standard, great ecosystem, type safety |
| **Bundler** | Vite | Fast, modern, HMR for development |
| **Styling** | Tailwind CSS v4 | Utility-first, modern, efficient, Vite plugin integration |
| **Code Quality** | ESLint + Prettier | Consistent code style, catch errors early |
| **State** | Zustand | Lightweight, simple alternative to Redux |
| **Data Fetching** | TanStack Query | Caching, deduplication, polling (critical for status) |
| **Package Manager** | npm | Standard, reliable dependency management |
| **Router** | React Router v6 | Standard for SPA routing |
| **PDF Rendering** | pdf.js | Lightweight, browser-native PDF viewer |
| **Auth** | Google OAuth (via FastAPI) | Simple, secure, no password management |

### 2.2 Frontend Project Structure

```
frontend/
├─ src/
│  ├─ components/
│  │  ├─ SignIn.tsx (Google OAuth sign-in button)
│  │  ├─ ReviewPanel.tsx (hero component - dual PDF viewer)
│  │  ├─ ToneSelector.tsx (tone presets + custom input)
│  │  ├─ EditPanel.tsx (inline text editor)
│  │  └─ ProgressIndicator.tsx (step-by-step progress)
│  ├─ pages/
│  │  ├─ AuthCallback.tsx (OAuth callback handler)
│  │  ├─ Upload.tsx
│  │  ├─ Processing.tsx
│  │  ├─ Review.tsx (HERO PAGE)
│  │  └─ NotFound.tsx
│  ├─ hooks/
│  │  ├─ useAuth.ts (Google OAuth state, token management)
│  │  ├─ useUpload.ts (file upload logic)
│  │  ├─ useTranslation.ts (polling status)
│  │  └─ usePDFViewer.ts (PDF rendering)
│  ├─ services/
│  │  └─ api.ts (fetch client, endpoints)
│  ├─ stores/
│  │  └─ appStore.ts (Zustand: user, currentJob, settings)
│  ├─ index.css (Tailwind CSS v4 import: @import "tailwindcss")
│  ├─ App.tsx (Router setup, auth flow)
│  └─ main.tsx (Entry point)
├─ public/
│  └─ index.html
├─ .eslintrc.cjs (ESLint configuration)
├─ .prettierrc (Prettier configuration)
├─ vite.config.ts (Vite + Tailwind CSS v4 plugin)
├─ tsconfig.json
├─ package.json
└─ .env.local (API_URL=http://localhost:8000)
```

### 2.3 Frontend Development Setup

**Tailwind CSS v4 Configuration:**
- Uses `@tailwindcss/vite` plugin for seamless Vite integration
- Single CSS import: `@import "tailwindcss"` in `src/index.css`
- No PostCSS configuration required
- No `tailwind.config.ts` needed (uses CSS-first configuration)
- All styling via utility classes (no native CSS files)

**Code Quality Tools:**
- **ESLint**: TypeScript + React linting with recommended rules
- **Prettier**: Code formatting with ESLint integration
- **Scripts**: `npm run lint`, `npm run lint:fix`, `npm run format`, `npm run format:check`

**Styling Approach:**
- Utility-first CSS with Tailwind CSS v4
- No component-level CSS files
- Consistent design system via Tailwind utilities
- Responsive design using Tailwind breakpoints

### 2.4 Key Frontend Components

**ReviewPanel (Hero Component):**
- Dual PDF viewers using pdf.js
- Synchronized scrolling (default ON, toggle OFF)
- Hover highlighting (block-level mapping)
- Responsive: Desktop (2-col) → Tablet (2-col) → Mobile (tabs)

**StatusPolling (TanStack Query):**
```typescript
// Poll job status every 2 seconds while processing
useQuery({
  queryKey: ['translation', jobId],
  queryFn: () => api.getStatus(jobId),
  refetchInterval: 2000,
  enabled: status !== 'complete',
})
```

**Authentication Flow (Google OAuth + JWT):**

**Installation:**
```bash
# Backend (dependencies already in pyproject.toml)
# google-auth, python-jose, httpx

# Frontend
# No additional auth library needed - custom implementation
```

**Backend Setup:**
```python
# backend/app/routers/auth.py
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt

@router.get("/api/v1/auth/google")
async def initiate_google_oauth():
    # Returns Google OAuth URL for frontend redirect
    
@router.post("/api/v1/auth/google/callback")
async def google_oauth_callback(callback: GoogleOAuthCallback):
    # Exchanges OAuth code for ID token
    # Verifies ID token with Google
    # Creates/updates user in database
    # Returns JWT access token

@router.get("/api/v1/auth/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Returns current user info from JWT token
```

**Frontend Flow:**
- User clicks "Sign in with Google" button
- Frontend calls `/api/v1/auth/google` to get OAuth URL
- Browser redirects to Google consent screen
- Google redirects to `/auth/callback` with auth code
- Frontend exchanges code via `/api/v1/auth/google/callback`
- Backend returns JWT token
- Frontend stores token in localStorage (httpOnly cookie enhancement possible)
- All API requests include `Authorization: Bearer <token>` header
- Token expiration detected and handled gracefully

**Implementation Details:**
- Custom `useAuth` hook manages authentication state
- Token persistence across page reloads
- Automatic token expiration detection (5-minute threshold)
- Graceful handling of expired/invalid tokens

### 2.4 State Management (Zustand)

```typescript
interface AppStore {
  // Auth
  user: {id, email, name, subscription} | null
  isAuthenticated: boolean
  login: (googleToken) => void
  logout: () => void

  // Current translation
  currentJob: {id, status, progress, file} | null
  setCurrentJob: (job) => void

  // UI
  reviewPanelSync: boolean
  toggleSync: () => void
  selectedBlock: {id, text} | null
  editMode: boolean
}
```

---

## 3. Backend Architecture

### 3.1 Backend Stack & Rationale

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

### 3.2 Backend Project Structure

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

### 3.3 API Endpoints (REST)

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

### 3.4 Database Schema

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

## 4. Data Processing Pipeline

### 4.1 PDF Extraction (PyMuPDF)

**Algorithm:**
```python
def extract_text_with_layout(pdf_path):
    doc = fitz.open(pdf_path)
    results = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # Get text with block layout information
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if block["type"] == 0:  # Text block
                results.append({
                    "page": page_num,
                    "text": block["lines"],
                    "bbox": block["bbox"],  # Coordinates for reconstruction
                    "type": "text"
                })
            elif block["type"] == 1:  # Image
                results.append({
                    "page": page_num,
                    "bbox": block["bbox"],
                    "type": "image"
                })
    
    return results
```

**Performance:**
- 50-200 pages/second on typical server
- 500-page document: ~3-10 seconds

### 4.2 Translation Pipeline (Batching)

**Strategy:**
- Group extracted text blocks by page
- Batch translate 10 blocks at once (DeepL API efficiency)
- Parallelize across pages using Celery

```python
async def translate_blocks(blocks, target_language):
    for page_blocks in batch_by_page(blocks):
        futures = []
        for block_batch in batch(page_blocks, size=10):
            texts = [b["text"] for b in block_batch]
            future = await deepl.translate_async(
                texts,
                target_lang=target_language
            )
            futures.append(future)
        
        # Await all futures for this page
        results = await asyncio.gather(*futures)
```

**Cost & Time:**
- DeepL: ~$0.15 per 100k words
- 100-page document (50k words): ~$0.075
- Processing time: 30-60 seconds

### 4.3 Tone Customization (Claude Haiku)

**When Applied:**
- Initial translation complete → Default tone (neutral)
- User clicks tone preset → Re-apply with tone
- Uses Claude 3.5 Haiku (lightweight, fast)

**Example Prompt:**
```
Current translation: "The system works well."
Target tone: Creative
Target context: Novel translation

Rewrite this translation in the target tone, preserving all meaning:
"The system works well."

Return ONLY the rewritten text.
```

**Response:**
```
The system hums with graceful efficiency.
```

**Cost & Time:**
- Claude Haiku: ~$0.80 per 1M input tokens
- 100 pages (~60k tokens): ~$0.048
- Processing: 15-30 seconds

### 4.4 PDF Reconstruction & Editing Flow

**Critical Decision: How to Handle User Edits**

When user edits a block AFTER translation, we have three options:

#### **Option A: In-Memory Edit Tracking (RECOMMENDED for MVP)**

**How it works:**
```python
# Frontend maintains edit state in Zustand store
edits = {
  "block_id_1": "User's edited translation",
  "block_id_5": "Another edit",
}

# When downloading, apply edits before generating PDF
def generate_download_pdf(original_blocks, translated_blocks, edits):
    final_blocks = translated_blocks.copy()
    
    for block_id, edited_text in edits.items():
        final_blocks[block_id]["text"] = edited_text
    
    return reconstruct_pdf_from_blocks(original_blocks, final_blocks)
```

**Performance:**
- ✅ Fast (edits stored in memory, no DB writes)
- ✅ Simple (no complex PDF manipulation)
- ✅ No rebuild until download
- ❌ Edits lost if user closes browser (acceptable for MVP)

**Cost:** $0 additional overhead

---

#### **Option B: Rebuild Just-Modified Block**

**How it works:**
```python
# When user edits a block, rebuild ONLY that block
def update_pdf_block(pdf_path, block_id, new_text):
    doc = fitz.open(pdf_path)
    page = doc[block_id["page"]]
    
    # Replace just this block's text
    # Preserve original fonts, colors, styling
    page.delete_text(block_id["bbox"])
    page.insert_text(block_id["bbox"], new_text)
    
    return doc  # Updated PDF
```

**Performance:**
- ✅ Medium complexity (one block at a time)
- ✅ Faster than full rebuild
- ✅ Changes visible immediately
- ❌ Still requires PDF manipulation (complex)

**Cost:** Minimal (just PDFBox operations)

---

#### **Option C: Full PDF Rebuild**

**How it works:**
```python
# Reconstruct entire PDF from scratch whenever user edits
def full_reconstruct_pdf(original, all_translated_blocks_with_edits):
    # Regenerate PDF from text + layout
    # EXPENSIVE - requires rebuilding all 500 pages
```

**Performance:**
- ❌ SLOW (rebuild entire 500-page PDF for one edit)
- ❌ High CPU cost (10-30 seconds)
- ❌ Not acceptable for user experience

---

### **RECOMMENDATION: Option A (In-Memory + Rebuild on Download)**

**Why:**
1. **MVP speed:** Get to launch fast (no complex PDF manipulation)
2. **Performance:** Instant edit feedback (no rebuild delay)
3. **Cost:** Minimal ($0 additional)
4. **Simplicity:** Just track edits in frontend state

**Implementation:**

**Frontend (React + Zustand):**
```typescript
interface EditStore {
  edits: Map<string, string>  // block_id → edited_text
  
  editBlock(blockId: string, newText: string) {
    this.edits.set(blockId, newText)
    // Show updated text immediately in ReviewPanel
  }
  
  async downloadPDF() {
    const response = await api.download(jobId, {
      edits: Array.from(this.edits.entries())  // Send edits to backend
    })
    // Download file
  }
}
```

**Backend (FastAPI):**
```python
@router.get("/api/v1/download/{job_id}")
async def download_translation(job_id: str, edits: List[Tuple[str, str]]):
    # Load original translated PDF
    translated = load_from_s3(job_id)
    
    # Apply edits
    for block_id, new_text in edits:
        translated[block_id]["text"] = new_text
    
    # Reconstruct with edits
    final_pdf = reconstruct_pdf(translated)
    
    return final_pdf
```

**Performance:**
- Edit feedback: Instant (just update Zustand state)
- Download: 5-15 seconds (rebuild with edits applied)
- User experience: Excellent (responsive editing, clean download)

---

### **Phase 2: Optimize Editing**

**If editing becomes a bottleneck:**
- Implement Option B (rebuild just-edited blocks)
- Or: Switch to HTML rendering (edit in HTML → export to PDF)
- Store edit history in database (undo/redo)

**For now:** Keep Option A, launch fast!

---

## 5. Infrastructure & Deployment

### 5.1 Local Development (Docker Compose)

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/transkeep
      REDIS_URL: redis://redis:6379
      DEEPL_API_KEY: ${DEEPL_API_KEY}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: transkeep
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/transkeep
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

**Local Development Workflow:**
```bash
# Start all services
docker-compose up

# Endpoints available:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs (Swagger)
```

### 5.2 Production Deployment (AWS)

**Infrastructure:**

| Component | AWS Service | Rationale |
|-----------|-------------|-----------|
| **Frontend** | CloudFront + S3 | CDN for React SPA, static assets |
| **Backend** | ECS (Fargate) | Containerized FastAPI, auto-scaling |
| **Database** | RDS PostgreSQL | Managed, replicated, backups |
| **Cache** | ElastiCache Redis | Managed Redis for Celery queue |
| **File Storage** | S3 | Scalable, cheap, CDN-integrated |
| **Jobs** | ECS Tasks | Celery workers as containerized tasks |
| **Secrets** | Secrets Manager | Store API keys, DB passwords |
| **Monitoring** | CloudWatch | Logs, metrics, alarms |
| **Load Balancing** | ALB | Distribute traffic to ECS tasks |

**Deployment Pipeline:**
```
1. Code pushed to GitHub
2. GitHub Actions triggers CI/CD
3. Build Docker image (backend & frontend)
4. Push to ECR (Elastic Container Registry)
5. Deploy to ECS:
   - Update backend service
   - Update Celery workers
   - Deploy static assets to S3
6. CloudFront invalidates cache
7. Health checks verify deployment
8. Monitoring alerts on failures
```

### 5.3 Scalability Strategy

**Horizontal Scaling (Auto-scaling):**
- Backend: ECS auto-scales based on CPU/memory
- Celery workers: Scale up during peak upload times
- Database: RDS read replicas for high query load (Phase 2)

**Rate Limiting:**
- Per-user: 10 requests/minute (prevent abuse)
- Per-tenant: 100 documents/month (freemium limit)
- S3: Automatic (AWS handles)

**Caching Strategy:**
- Redis: Cache user sessions, job status
- CloudFront: Cache download links (24 hours)
- Browser: Cache static assets with long TTL

---

## 6. Multi-Tenant Architecture

### 6.1 Data Isolation

**Tenant Context Extraction:**
```python
# Every request includes tenant_id (derived from user's subscription)
async def get_current_user(token: str) -> User:
    payload = verify_jwt(token)
    user_id = payload["sub"]
    
    # User is the tenant (MVP)
    # Later: User belongs to Tenant → Multi-user tenant (Phase 2)
    tenant_id = user_id
    
    return User(id=user_id, tenant_id=tenant_id)
```

**Query-Level Isolation:**
```python
# Every query includes tenant filter
async def get_translation(job_id: str, tenant_id: str):
    return await db.query(Translation).filter(
        Translation.job_id == job_id,
        Translation.tenant_id == tenant_id  # CRITICAL
    ).first()
```

**Storage-Level Isolation:**
```
S3 Structure:
s3://transkeep-bucket/
  ├─ uploads/
  │  ├─ {tenant_id}/
  │  │  ├─ {job_id}/
  │  │  │  └─ original.pdf
  ├─ translations/
  │  ├─ {tenant_id}/
  │  │  ├─ {job_id}/
  │  │  │  └─ translated.pdf
```

### 6.2 Multi-Tenant Roadmap

**MVP (User = Tenant):**
- One user account = One tenant
- Simple, secure, fast to build

**Phase 2 (Organization Tenants):**
- Team creates organization
- Multiple users share glossary, settings
- Role-based access (owner, editor, viewer)
- Shared billing

---

## 7. Security & Compliance

### 7.1 Authentication & Authorization

**Google OAuth Flow:**
```
1. User clicks "Sign in with Google"
2. Frontend redirects to Google OAuth consent screen
3. User approves → Google redirects to backend with code
4. Backend exchanges code for ID token
5. Backend verifies token signature (Google public key)
6. Backend creates user in DB if first time
7. Backend generates JWT token
8. Frontend stores JWT in localStorage (or httpOnly cookie)
9. All API requests include Authorization header
```

**JWT Token:**
```
Header: {alg: "HS256", typ: "JWT"}
Payload: {sub: "user_id", tenant_id, exp: now + 7days, iat: now}
Signature: HMAC(header.payload, SECRET_KEY)
```

**Token Refresh:**
- Token expires in 7 days
- Frontend detects expired token (401 response)
- Redirects to re-authenticate with Google
- No refresh token (for simplicity)

### 7.2 Data Security

**In Transit:**
- All connections HTTPS/TLS
- Certificate from AWS Certificate Manager
- Enforced by ALB (no unencrypted traffic)

**At Rest:**
- PostgreSQL: Encrypted by RDS
- S3: Encrypted with AWS KMS
- Redis: Encrypted by ElastiCache

**File Handling:**
- PDF uploads: Virus scan via AWS Macie (Phase 2)
- Temp files: Deleted after 24 hours
- No permanent document storage (except user downloads)

### 7.3 Privacy & GDPR

**Data Retention:**
- User's original PDF: Deleted after 1 hour (MVP), 24 hours (Phase 2)
- Translation result: Available for 24 hours for download
- Permanent storage: Only if user requests saved project (Phase 2)

**User Data Export:**
- Endpoint: GET /api/v1/export (export all user's data)
- Format: JSON with metadata, no raw PDFs (too large)

**Right to Delete:**
- Endpoint: DELETE /api/v1/user/delete-account
- Cascades: Delete user, all translations, all files
- Processed asynchronously (via Celery job)

---

## 8. Error Handling & Resilience

### 8.1 Error Categories & Responses

| Error | HTTP Status | User Message | Action |
|-------|-------------|--------------|--------|
| Invalid file format | 400 | "Please upload a PDF file" | Retry with valid file |
| File too large | 413 | "File exceeds 100MB limit" | Split file |
| Unauthorized (no token) | 401 | "Please sign in" | Redirect to login |
| Quota exceeded | 429 | "You've used your free documents" | Upgrade subscription |
| Processing failed | 500 | "Translation failed. Retry?" | Retry from upload |
| Download expired | 410 | "Download link expired" | Re-upload to translate again |
| Network timeout | 504 | "Server busy. Please try again" | Retry (transparent to user) |

### 8.2 Retry Logic (Client & Server)

**Client-side (Exponential Backoff):**
```typescript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fetch(url, options)
    } catch (error) {
      const delay = Math.pow(2, attempt) * 1000 // 1s, 2s, 4s
      if (attempt < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay))
      } else {
        throw error
      }
    }
  }
}
```

**Server-side (Celery Task Retry):**
```python
@celery_app.task(bind=True, max_retries=3)
def extract_translate(self, job_id):
    try:
        # Process
    except Exception as exc:
        # Exponential backoff: 60s, 120s, 300s
        self.retry(countdown=60 * (2 ** self.request.retries), exc=exc)
```

### 8.3 Graceful Degradation

**If DeepL API Down:**
- Fall back to Google Translate API (lower quality)
- Notify user: "Using backup translation service (lower quality)"
- Alert ops team

**If Claude API Down (Tone):**
- Skip tone customization
- Deliver base translation only
- Notify user: "Tone customization temporarily unavailable"

**If S3 Down:**
- Buffer in Redis
- Retry periodically (every 30s for 24 hours)
- Alert ops team

---

## 9. Monitoring & Observability

### 9.1 Key Metrics to Track

**Business Metrics:**
- Daily active users (DAU)
- Total documents translated
- Freemium to paid conversion rate
- Average translation time
- User satisfaction (NPS)

**Technical Metrics:**
- API response times (p50, p95, p99)
- Error rates (by endpoint, by error type)
- Job processing time (extract, translate, tone, reconstruct)
- Worker queue depth (Celery pending jobs)
- S3 upload/download bandwidth
- Database connection pool usage

**System Metrics:**
- CPU/memory utilization (ECS tasks)
- Database disk usage
- Redis memory usage
- Network I/O

### 9.2 Logging Strategy (OpenTelemetry Protocol)

**OpenTelemetry (Otel) Implementation:**
- Use Otel protocol for vendor-agnostic observability
- Backend: `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp`
- Workers: `opentelemetry-instrumentation-celery`
- Frontend: `@opentelemetry/api` + exporters
- Flexibility: Switch backends (CloudWatch → Datadog → Jaeger) without code changes

**Installation:**
```bash
# Backend
pip install opentelemetry-api opentelemetry-sdk
pip install opentelemetry-instrumentation-fastapi
pip install opentelemetry-exporter-otlp
pip install opentelemetry-instrumentation-sqlalchemy
pip install opentelemetry-instrumentation-requests

# Celery workers
pip install opentelemetry-instrumentation-celery

# Frontend
npm install @opentelemetry/api @opentelemetry/sdk-web
npm install @opentelemetry/auto-instrumentations-web
npm install @opentelemetry/exporter-trace-otlp-http
```

**Log Levels:**
- DEBUG: Development only, detailed flow
- INFO: Key milestones (user login, job started, job completed)
- WARNING: Recoverable issues (retry attempt, degraded service)
- ERROR: Problems (API failure, DB error)

**Log Structure (JSON with Otel trace/span IDs):**
```json
{
  "timestamp": "2025-11-14T10:30:45Z",
  "level": "INFO",
  "service": "backend",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "user_id": "uuid",
  "tenant_id": "uuid",
  "job_id": "uuid",
  "action": "translation_started",
  "duration_ms": 125,
  "details": {
    "file_size_mb": 2.4,
    "language_pair": "en_ja",
    "page_count": 45
  }
}
```

**Otel Exporter Configuration:**
```python
# backend/app/config.py
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4318/v1/traces"  # Local: Jaeger
    # For AWS: endpoint="http://otel-collector.local:4318/v1/traces"
)

trace_provider = TracerProvider()
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
```

**CloudWatch Integration (via Otel Collector):**
- Deploy Otel Collector in ECS
- Collector receives traces via OTLP protocol
- Exporter sends to CloudWatch Logs + CloudWatch Metrics + X-Ray
- Alarms: Error rate > 5%, Response time p99 > 5s, Queue depth > 100
- Vendor flexibility: Can also export to Datadog, New Relic, etc.

---

## 10. Deployment Checklist

### Pre-Launch

- [ ] Database migrations tested (Alembic)
- [ ] Environment variables configured (Secrets Manager)
- [ ] API endpoints load-tested (200+ concurrent users)
- [ ] Celery workers tested (process 500-page PDFs)
- [ ] OAuth flow tested (sign-in, sign-out, token refresh)
- [ ] S3 permissions configured (least privilege)
- [ ] CloudFront cache settings correct
- [ ] SSL certificate installed & valid
- [ ] DNS records pointing to ALB
- [ ] Error pages (404, 500) deployed
- [ ] Monitoring alerts configured
- [ ] Backup strategy documented (RDS automated backups)
- [ ] Disaster recovery plan (what if RDS fails?)

### Launch Day

- [ ] Start ECS services (1 frontend task, 2 backend tasks, 2 workers)
- [ ] Verify health checks passing
- [ ] Monitor logs for errors (first 30 min)
- [ ] Test download functionality manually
- [ ] Send announcement to beta testers
- [ ] Stand by for support (first 2 hours)
- [ ] Auto-scaling tested (trigger high load)

---

## 11. Next Steps & Timeline

### Week 1: Setup & Scaffolding
- [ ] Create repositories (frontend, backend)
- [ ] Set up Docker development environment
- [ ] Initialize React app (Vite)
- [ ] Initialize FastAPI project
- [ ] Set up Celery + Redis locally
- [ ] Create PostgreSQL schema

### Week 2: Core Features
- [ ] Implement Google OAuth
- [ ] Build upload endpoint (chunked upload to S3)
- [ ] Build PDF extraction (PyMuPDF)
- [ ] Integrate DeepL API
- [ ] Build status polling endpoint
- [ ] Create ReviewPanel UI component

### Week 3: Polish & Deploy
- [ ] Integrate Claude Haiku for tone
- [ ] Build tone selector UI
- [ ] Build edit panel
- [ ] Download functionality
- [ ] Error handling & edge cases
- [ ] Deploy to AWS (ECS, RDS, S3)
- [ ] Final QA & bug fixes

### Week 4: Launch & Monitor
- [ ] Beta launch (50 users)
- [ ] Monitor logs & metrics
- [ ] Fix critical bugs
- [ ] Gather feedback
- [ ] Iterate based on early usage
- [ ] Public launch

---

## 12. Architecture Decisions Reference

### Decision Records

**D1: Async Job Processing**
- **Rationale:** Large PDFs (100MB) would timeout if processed synchronously
- **Choice:** Celery + Redis for background jobs
- **Tradeoff:** Added complexity vs MVP simplicity (justified by requirement)

**D2: Multi-Tenant from Day 1**
- **Rationale:** Enterprise roadmap requires multi-tenant architecture
- **Choice:** User = tenant (MVP), organization = tenant (Phase 2)
- **Benefit:** Prevents architectural rewrites later

**D3: PDFs Deleted After 24 Hours**
- **Rationale:** Privacy (no permanent storage), cost (S3 expenses)
- **Choice:** Temporary storage only
- **Tradeoff:** Users can't access old translations (minor for MVP)

**D4: PostgreSQL for Metadata Only**
- **Rationale:** Don't store large BLOBs in DB
- **Choice:** S3 for files, PostgreSQL for metadata
- **Benefit:** Fast queries, scalable storage

**D5: CloudFront CDN**
- **Rationale:** PDF downloads must be fast globally
- **Choice:** S3 + CloudFront (3-day cache)
- **Benefit:** Downloads from 200+ edge locations worldwide

**D6: Google OAuth Only**
- **Rationale:** Simplify authentication, no password management
- **Choice:** No email/password signup
- **Tradeoff:** Users must have Google account (acceptable for MVP)

---

## Appendix: Technology Cheat Sheet

**Frontend:**
```bash
npm create vite@latest -- --template react-ts
npm install react-router-dom @tanstack/react-query zustand
npm install -D @tailwindcss/vite tailwindcss@next
npm install -D eslint @typescript-eslint/eslint-plugin @typescript-eslint/parser eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier eslint-plugin-prettier
npm install pdfjs-dist
```

**Backend:**
```bash
pip install fastapi uvicorn pydantic sqlalchemy psycopg2-binary
pip install celery redis
pip install PyMuPDF deepl anthropic
pip install python-jose google-auth google-auth-oauthlib
pip install alembic
```

**Infrastructure:**
```bash
# AWS CLI commands
aws ecr create-repository --repository-name transkeep
aws rds create-db-instance --db-instance-identifier transkeep-db
aws s3 mb s3://transkeep-bucket
aws iam create-role --role-name ECSTaskRole
```

---

**Status:** Ready for Sprint Planning & Development  
**Created:** November 14, 2025  
**Track:** Enterprise Method - Greenfield  
**MVP Timeline:** 1 month

