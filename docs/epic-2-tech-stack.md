# Epic 2: Core Translation Pipeline - Tech Stack & Architecture

**Epic:** 2  
**Title:** Core Translation Pipeline 🔄  
**Stories:** 2.1 - 2.5  
**Duration:** 5 days (Dec 9-13)  
**Status:** contexted  
**Created:** November 15, 2025

---

## Overview

Implement the complete translation pipeline: file upload, PDF extraction, translation via DeepL, task orchestration with Celery, and real-time status tracking.

---

## 📦 Tech Stack by Component

### **File Upload & Storage Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Upload Handler** | FastAPI File | Built-in | Type-safe multipart uploads | Story 2.1 |
| **File Validation** | Pydantic BaseModel | 2.5+ | Request validation | Story 2.1 |
| **S3 Client** | boto3 | 1.29+ | AWS SDK for Python | Story 2.1 |
| **Local S3** | MinIO | Latest | S3-compatible local storage | Story 2.1 (dev) |
| **Prod S3** | AWS S3 | - | Production file storage | Story 2.1 (prod) |
| **Chunked Upload** | Python streams | - | Handle 100MB files efficiently | Story 2.1 |
| **Async Upload** | aiofiles | Latest | Non-blocking file I/O | Story 2.1 |

### **PDF Processing Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **PDF Library** | PyMuPDF (fitz) | 1.23+ | Fast text extraction with coordinates | Story 2.2 |
| **Text Extraction** | PyMuPDF blocks | - | Per-page block extraction | Story 2.2 |
| **Coordinate System** | Normalized percentages | - | Layout-preserving coordinates | Story 2.2 |
| **Performance** | Multi-threading | - | Parallel page processing | Story 2.2 |
| **Caching** | Redis | 7 | Cache extracted blocks (24h) | Story 2.2 |
| **Memory** | Generators | - | Stream large PDFs | Story 2.2 |

### **Translation API Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Translation API** | DeepL Python Client | 1.16+ | High-quality translations | Story 2.3 |
| **Supported Languages** | EN→JA, EN→VI, EN→ZH | - | User-selected languages | Story 2.3 |
| **Batch Processing** | DeepL Batch API | - | 10 blocks per API call | Story 2.3 |
| **Error Handling** | Retry logic | - | Exponential backoff on rate limit | Story 2.3 |
| **Cost Tracking** | Custom logging | - | Track API costs per document | Story 2.3 |
| **Budget** | $0.15 per job | - | 3 translations max per user/day | Story 2.3 |

### **Task Queue Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Task Queue** | Celery | 5.3+ | Distributed async tasks | Story 2.4 |
| **Message Broker** | Redis | 7 | Celery broker communication | Story 2.4 |
| **Task Orchestration** | Celery Signatures | - | Chain extraction → translate → tone → reconstruct | Story 2.4 |
| **Error Handling** | Celery Retry | - | Automatic retry with backoff | Story 2.4 |
| **Monitoring** | Celery Events | - | Real-time task monitoring | Story 2.4 |
| **Flower UI** | Flower | Latest | Web-based task monitoring | Story 2.4 |
| **Worker Pool** | prefork | - | Process pool for parallelization | Story 2.4 |

### **Job Status Tracking Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Status Storage** | PostgreSQL | 15 | Persistent job status | Story 2.5 |
| **Status Model** | SQLAlchemy ORM | 2.0+ | Type-safe status queries | Story 2.5 |
| **Status Updates** | Celery Task Hooks | - | Update status after each step | Story 2.5 |
| **Progress Calculation** | SQL Queries | - | Count processed vs total blocks | Story 2.5 |
| **ETA Calculation** | Custom formula | - | Estimate time to completion | Story 2.5 |
| **Frontend Polling** | TanStack Query | Latest | Efficient polling with caching | Story 2.5 |
| **Polling Interval** | 2 seconds | - | Real-time progress updates | Story 2.5 |

---

## 🔄 Epic 2 Story & Tech Stack Mapping

### **Story 2.1: File Upload Endpoint**
```
Technologies:
├── FastAPI (multipart upload)
├── Pydantic (request validation)
├── boto3 (S3 upload)
├── PostgreSQL (translation record)
├── SQLAlchemy (ORM)
└── Error handling & validation
```

**Key Files:**
- `backend/app/routers/upload.py` - Upload endpoint
- `backend/app/schemas/upload.py` - Request/response models
- `backend/app/services/s3_service.py` - S3 operations
- `backend/tests/test_upload.py` - Integration tests

### **Story 2.2: PDF Extraction with PyMuPDF**
```
Technologies:
├── PyMuPDF (text extraction)
├── Redis (block caching)
├── Multi-threading (parallelization)
├── PostgreSQL (block storage)
└── SQLAlchemy (ORM)
```

**Key Files:**
- `backend/app/services/pdf_service.py` - PDF extraction
- `backend/app/tasks/extract_pdf.py` - Celery task
- `backend/app/schemas/pdf.py` - Block data models
- `backend/tests/test_pdf_extraction.py` - Tests

### **Story 2.3: DeepL Translation Integration**
```
Technologies:
├── DeepL API client (translation)
├── Batch processing (10 blocks/call)
├── Celery (async tasks)
├── Error handling (rate limit retry)
└── Cost tracking (logging)
```

**Key Files:**
- `backend/app/services/translation_service.py` - DeepL wrapper
- `backend/app/tasks/translate_blocks.py` - Translation task
- Cost tracking in logs & database

### **Story 2.4: Celery Job Queue Setup**
```
Technologies:
├── Celery (task orchestration)
├── Redis (broker)
├── SQLAlchemy (status persistence)
├── Flower (monitoring)
└── Task chains (workflow)
```

**Key Files:**
- `backend/app/celery_app.py` - Celery configuration
- `backend/app/tasks/*.py` - All task definitions
- Pipeline: extract → translate → tone → reconstruct

### **Story 2.5: Status Polling Endpoint**
```
Technologies:
├── FastAPI (GET /status/{job_id})
├── PostgreSQL (status queries)
├── SQLAlchemy (ORM)
├── TanStack Query (frontend polling)
└── Real-time progress UI
```

**Key Files:**
- `backend/app/routers/translation.py` - Status endpoint
- `frontend/src/hooks/useTranslation.ts` - Status polling hook
- `frontend/src/pages/ProcessingPage.tsx` - Progress UI

---

## 📊 Data Flow Architecture

### **Complete Translation Pipeline**

```
1. USER UPLOADS PDF
   └─ FastAPI endpoint receives multipart upload
   └─ Pydantic validates file (type, size)
   └─ boto3 uploads to S3
   └─ SQLAlchemy creates Translation record (status='pending')
   └─ Returns job_id to frontend
   └─ Triggers extract_and_translate Celery task

2. EXTRACT PDF BLOCKS
   ├─ Celery task: extract_pdf_task(job_id)
   ├─ PyMuPDF reads PDF from S3
   ├─ Extracts text blocks with coordinates
   ├─ Stores in Redis cache (TTL 24h)
   ├─ Updates DB: DocumentBlocks table
   ├─ Updates status: 'extracting' → 'extracted'
   └─ Yields to next task in chain

3. TRANSLATE BLOCKS
   ├─ Celery task: translate_blocks_task(job_id)
   ├─ Gets blocks from Redis cache
   ├─ Batches 10 blocks per API call
   ├─ Calls DeepL API (EN→JA/VI/ZH)
   ├─ Stores translations in DocumentBlocks
   ├─ Updates status: 'translating' → 'translated'
   ├─ Tracks API costs in logs
   └─ Yields to next task in chain

4. CUSTOMIZE TONE (Optional)
   ├─ Celery task: customize_tone_task(job_id)
   ├─ Gets translations from DB
   ├─ Calls Claude Haiku API with tone prompt
   ├─ Updates translations with tone version
   ├─ Updates status: 'tone_customizing' → 'tone_customized'
   └─ Yields to final task

5. RECONSTRUCT PDF
   ├─ Celery task: reconstruct_pdf_task(job_id)
   ├─ Gets original PDF from S3
   ├─ Gets final translations from DB
   ├─ PyMuPDF reconstructs with new text
   ├─ Uploads final PDF to S3
   ├─ Updates status: 'reconstructing' → 'completed'
   └─ Task chain completes

6. FRONTEND POLLS STATUS
   ├─ TanStack Query every 2 seconds
   ├─ GET /api/v1/status/{job_id}
   ├─ Receives: status, progress%, ETA
   ├─ Updates ProcessingPage UI
   ├─ Stops polling when status='completed'
   └─ Redirects to ReviewPage
```

---

## 🗄️ Database Schema for Epic 2

### **Translations Table**
```sql
CREATE TABLE translations (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  status VARCHAR(50),  -- pending, extracting, extracted, translating, translated, tone_customizing, tone_customized, reconstructing, completed, failed
  progress_percent INT DEFAULT 0,
  total_blocks INT,
  processed_blocks INT,
  original_pdf_path VARCHAR(500),
  translated_pdf_path VARCHAR(500),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP,
  completed_at TIMESTAMP,
  error_message TEXT,
  deeplapi_cost DECIMAL(10, 6),
  claude_cost DECIMAL(10, 6)
);
```

### **DocumentBlocks Table**
```sql
CREATE TABLE document_blocks (
  id UUID PRIMARY KEY,
  translation_id UUID NOT NULL REFERENCES translations(id) ON DELETE CASCADE,
  page_number INT NOT NULL,
  block_number INT NOT NULL,
  original_text TEXT NOT NULL,
  translated_text TEXT,
  tone_customized_text TEXT,
  coordinates JSONB,  -- {x, y, width, height}
  font_size INT,
  is_processed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_translation_id ON document_blocks(translation_id);
CREATE INDEX idx_page_block ON document_blocks(translation_id, page_number, block_number);
```

---

## 🚀 Deployment Configuration

### **Local Development (Docker Compose)**
```yaml
services:
  backend:
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/transkeep
      - REDIS_URL=redis://redis:6379
      - DEEPL_API_KEY=${DEEPL_API_KEY}
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
  
  celery_worker:
    command: celery -A app.celery_app worker -l info
    depends_on:
      - redis
      - postgres

  flower:
    image: mher/flower:latest
    ports:
      - 5555:5555
    environment:
      - CELERY_BROKER_URL=redis://redis:6379
```

### **Production (AWS)**
- **Backend:** ECS Fargate with Celery workers
- **Database:** RDS PostgreSQL (multi-AZ)
- **Cache:** ElastiCache Redis (cluster mode enabled)
- **File Storage:** S3 buckets with lifecycle policies (delete after 24h)
- **Monitoring:** CloudWatch logs + metrics
- **API Keys:** AWS Secrets Manager

---

## 📋 API Endpoints for Epic 2

### **Story 2.1: Upload**
```
POST /api/v1/upload
  Content-Type: multipart/form-data
  Body: file (PDF)
  Response: {
    "job_id": "uuid",
    "status": "pending",
    "message": "File uploaded successfully"
  }
```

### **Story 2.5: Status**
```
GET /api/v1/status/{job_id}
  Response: {
    "job_id": "uuid",
    "status": "translating",
    "progress": 45,
    "total_blocks": 100,
    "processed_blocks": 45,
    "eta_seconds": 120,
    "page_count": 10
  }
```

---

## 🎯 Success Criteria for Epic 2

**All stories in Epic 2 must satisfy:**

- ✅ Upload PDF up to 100MB reliably
- ✅ Extract text blocks with accurate coordinates
- ✅ Translate via DeepL with batch optimization
- ✅ Celery pipeline orchestrates all tasks
- ✅ Status updates in real-time
- ✅ Works for 10, 100, 500+ page PDFs
- ✅ Processing time: 10-90 seconds depending on size
- ✅ Error recovery and retry working
- ✅ Costs tracked and logged
- ✅ Flower monitoring available
- ✅ All tests passing
- ✅ No data loss on failures

---

## 📚 External Resources

- [DeepL Python Docs](https://github.com/DeepLcom/deepl-python)
- [Celery Documentation](https://docs.celeryproject.io)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io)
- [boto3 S3 Reference](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [Flower Monitoring](https://flower.readthedocs.io)

---

**Epic 2 Tech Stack Status:** ✅ **CONTEXTED**

All technologies identified for Stories 2.1-2.5.
Ready for implementation.

**Created:** November 15, 2025  
**Last Updated:** November 15, 2025

