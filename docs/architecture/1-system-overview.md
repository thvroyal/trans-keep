# 1. System Overview

## 1.1 High-Level Architecture Diagram

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

## 1.2 Request Flow: Upload to Download

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
