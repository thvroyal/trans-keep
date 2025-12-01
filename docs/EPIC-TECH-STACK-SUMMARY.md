# Epic Tech Stack Summary - All Epics Contexted

**Created:** November 15, 2025  
**Status:** ✅ All 4 Epics Contexted  
**Coverage:** 100% of stories have tech stack documentation

---

## Overview

Complete technical specification for all 4 epics of the TransKeep MVP. Each epic has a dedicated tech stack document detailing all technologies, versions, and usage patterns.

---

## 📋 Epic Tech Stack Documents

### **Epic 1: Setup & Scaffolding** 🏗️
**File:** `docs/epic-1-tech-stack.md`  
**Stories:** 1.1-1.5  
**Focus:** Development environment, frameworks, CI/CD

**Key Technologies:**
- Frontend: React 18, TypeScript, Vite, shadcn/ui, Tailwind
- Backend: FastAPI, Python 3.11, uv, PostgreSQL, Redis
- Infrastructure: Docker, Docker Compose, GitHub Actions
- Observability: OpenTelemetry, Jaeger
- Auth: better-auth, Google OAuth

**Key Outputs:**
- Two repositories ready (frontend, backend)
- Docker Compose with 7 services
- PostgreSQL schema
- GitHub Actions CI/CD pipelines
- Authentication working (sign-in/out)
- Observability configured (Jaeger)

---

### **Epic 2: Core Translation Pipeline** 🔄
**File:** `docs/epic-2-tech-stack.md`  
**Stories:** 2.1-2.5  
**Focus:** File handling, PDF processing, translation, job queue

**Key Technologies:**
- Upload: FastAPI multipart, boto3 (S3), streaming
- PDF: PyMuPDF (fitz), coordinate extraction
- Translation: DeepL API, batch processing
- Queue: Celery, Redis broker, task chains
- Polling: TanStack Query, real-time updates

**Key Outputs:**
- File upload endpoint (100MB max)
- PDF extraction with coordinates
- DeepL integration (3 languages)
- Celery pipeline (extract → translate → tone → reconstruct)
- Real-time status polling
- Error handling & retries

---

### **Epic 3: UI Polish & Refinement** ✨
**File:** `docs/epic-3-tech-stack.md`  
**Stories:** 3.1-3.5  
**Focus:** User experience, PDF rendering, edits, AI customization

**Key Technologies:**
- PDF Rendering: pdf.js, virtualization, canvas
- UI: React 18, shadcn/ui, Tailwind CSS
- State: Zustand (edit tracking)
- AI: Claude Haiku API (tone customization)
- UX: Error boundaries, fallbacks, retry logic

**Key Outputs:**
- Dual PDF viewer (side-by-side)
- Synchronized scrolling
- Hover highlighting
- Tone customization (5 presets + custom)
- Edit & alternatives workflow
- PDF download with edits
- Comprehensive error handling

---

### **Epic 4: Launch Prep & Beta** 🚀
**File:** `docs/epic-4-tech-stack.md`  
**Stories:** 4.1-4.5  
**Focus:** Production deployment, performance, security, QA

**Key Technologies:**
- AWS: ECS, RDS, ElastiCache, S3, CloudFront, CloudWatch
- Testing: pytest, Vitest, Playwright, k6 (load)
- Security: TLS, CORS, JWT, WAF, audit logs
- QA: Unit, integration, E2E, cross-browser, mobile
- Support: Email, feedback forms, status page, analytics

**Key Outputs:**
- AWS production deployment
- Auto-scaling configuration
- Performance optimization (200+ concurrent)
- Security audit passed
- Complete test coverage
- 50 beta users launched
- 24/7 monitoring active

---

## 🛠️ Technology by Category

### **Frontend Technologies**

| Layer | Technology | Version | Epic | Stories |
|-------|-----------|---------|------|---------|
| **Framework** | React | 18 | 1, 3 | 1.4, 3.1-3.5 |
| **Language** | TypeScript | 5.x | 1, 3 | 1.4, 3.1-3.5 |
| **Bundler** | Vite | 5.x | 1 | 1.1, 1.4 |
| **Styling** | Tailwind CSS | 3.x | 1, 3 | 1.4, 3.1-3.5 |
| **Components** | shadcn/ui | Latest | 1, 3 | 1.4, 3.1-3.5 |
| **Routing** | React Router | 6.x | 1 | 1.4 |
| **State** | Zustand | Latest | 1, 3 | 1.4, 3.3 |
| **HTTP** | TanStack Query | Latest | 2, 3 | 2.5, 3.1-3.5 |
| **PDF** | pdf.js | 4.x | 3 | 3.1 |
| **Package Mgr** | npm | 10+ | 1 | 1.1 |

### **Backend Technologies**

| Layer | Technology | Version | Epic | Stories |
|-------|-----------|---------|------|---------|
| **Runtime** | Python | 3.11 | 1, 2, 3, 4 | All |
| **Package Mgr** | uv | Latest | 1, 2 | 1.1-1.2, 2.1-2.4 |
| **Framework** | FastAPI | 0.104+ | 1, 2 | 1.2, 2.1, 2.5 |
| **Server** | Uvicorn | 0.24+ | 1 | 1.2 |
| **ORM** | SQLAlchemy | 2.0+ | 1, 2 | 1.2, 2.1, 2.5 |
| **Migrations** | Alembic | 1.12+ | 1, 2 | 1.2 |
| **Queue** | Celery | 5.3+ | 2 | 2.3-2.4 |
| **Translation** | DeepL | 1.16+ | 2 | 2.3 |
| **Tone** | Claude API | Latest | 3 | 3.2-3.3 |
| **PDF** | PyMuPDF | 1.23+ | 2, 3 | 2.2, 3.4 |
| **S3** | boto3 | 1.29+ | 2, 4 | 2.1, 3.4, 4.1 |

### **Infrastructure Technologies**

| Layer | Technology | Usage | Epic | Stories |
|-------|-----------|-------|------|---------|
| **Container** | Docker | Local & prod | 1, 4 | 1.1, 4.1 |
| **Orchestration** | Docker Compose | Local dev | 1 | 1.1 |
| **Orchestration** | AWS ECS | Production | 4 | 4.1 |
| **Database** | PostgreSQL | Primary DB | 1, 2, 4 | 1.2, 2.1, 4.1 |
| **Cache** | Redis | Session & queue | 1, 2, 3 | 1.2, 2.2-2.4, 3.2 |
| **Storage** | S3 / MinIO | File storage | 2, 4 | 2.1, 3.4, 4.1 |
| **CDN** | CloudFront | Content delivery | 4 | 4.1 |
| **CI/CD** | GitHub Actions | Pipelines | 1, 4 | 1.1, 4.1 |
| **Monitoring** | OpenTelemetry | Tracing | 1 | 1.5 |
| **Monitoring** | Jaeger | Visualization | 1 | 1.5 |
| **Monitoring** | CloudWatch | Production logs | 4 | 4.1, 4.2 |

### **Third-Party Services**

| Service | Purpose | API | Epic |
|---------|---------|-----|------|
| **Google OAuth** | User authentication | OAuth 2.0 | 1 |
| **DeepL** | Translation | REST API | 2 |
| **Claude** | Tone customization | REST API | 3 |
| **AWS** | Infrastructure | AWS SDK | 4 |
| **GitHub Actions** | CI/CD | YAML workflows | 1, 4 |

---

## 📊 Technology Stack Complexity

### **By Layer**

```
Frontend (React)
├─ Component Library (shadcn/ui)
├─ State Management (Zustand)
├─ Routing (React Router)
├─ Data Fetching (TanStack Query)
├─ PDF Rendering (pdf.js)
└─ Styling (Tailwind + CSS)

Backend (FastAPI)
├─ API Routes & Validation
├─ ORM (SQLAlchemy)
├─ Database Migrations (Alembic)
├─ Task Queue (Celery)
├─ File Storage (S3 / MinIO)
├─ External APIs (DeepL, Claude, Google)
└─ Observability (OpenTelemetry)

Infrastructure
├─ Local: Docker Compose
├─ CI/CD: GitHub Actions
├─ Production: AWS (ECS, RDS, ElastiCache, S3, CloudFront)
└─ Monitoring: CloudWatch
```

### **By Dependency**

```
Total Dependencies:
├─ Frontend: ~50 npm packages
├─ Backend: ~90 Python packages
└─ Infrastructure: 5 AWS services

Zero Custom Builds:
├─ All libraries are battle-tested
├─ All versions LTS or stable
├─ All technologies are open-source (except AWS)
└─ All have production usage
```

---

## 🔄 Technology Integration Points

### **Frontend ↔ Backend**

```
1. File Upload
   Frontend: File drop zone → FormData
   Backend: FastAPI multipart → boto3 → S3

2. Status Polling
   Frontend: TanStack Query (2s interval)
   Backend: GET /api/v1/status → DB query

3. Tone Customization
   Frontend: Button click with tone selection
   Backend: POST request → Claude API → DB update

4. Edit Submission
   Frontend: Zustand edits → POST
   Backend: Receive edits → PDF reconstruction → S3

5. PDF Download
   Frontend: Download button
   Backend: Apply edits → PyMuPDF → Pre-signed URL
```

### **Backend ↔ Database**

```
1. SQLAlchemy ORM
   Models: User, Translation, DocumentBlocks
   Queries: Indexed on translation_id, status

2. Alembic Migrations
   Version control: db/migrations/
   Run: `alembic upgrade head`

3. Connection Pooling
   FastAPI: SQLAlchemy connection pool
   Celery: Separate connection pool
   Max connections: 20 (production)
```

### **Backend ↔ Cache**

```
1. Redis Session Cache
   Login: Token stored in Redis (24h TTL)
   
2. PDF Blocks Cache
   Extract: Blocks stored in Redis (24h TTL)
   Hit rate target: >90%

3. Celery Broker
   Messages: Task jobs in Redis queue
```

### **Backend ↔ Celery Queue**

```
1. Task Chain
   extract_pdf() → translate_blocks() → customize_tone() → reconstruct_pdf()
   
2. Error Handling
   Retry: exponential backoff (2^n seconds)
   Max retries: 3
   
3. Monitoring
   Flower UI: localhost:5555 (dev)
   CloudWatch: production
```

---

## ✅ Tech Stack Validation

### **Completeness**

- ✅ 4 Epics with 20 stories
- ✅ All stories have tech documentation
- ✅ Frontend technologies identified
- ✅ Backend technologies identified
- ✅ Infrastructure documented
- ✅ Deployment architecture defined
- ✅ Integration points mapped
- ✅ External APIs documented

### **Production Readiness**

- ✅ All major frameworks are LTS/stable
- ✅ All languages have latest versions
- ✅ Database and cache have backups
- ✅ Authentication secure (OAuth + JWT)
- ✅ Monitoring and logging configured
- ✅ Error handling and retry logic
- ✅ Performance targets set
- ✅ Security audit checklist ready

### **Scalability**

- ✅ Frontend: Static files on CloudFront (infinite scalability)
- ✅ Backend: Horizontal scaling with ECS/Fargate
- ✅ Database: RDS multi-AZ with read replicas (optional)
- ✅ Cache: ElastiCache cluster mode (sharding)
- ✅ Queue: Celery can run unlimited workers
- ✅ Storage: S3 infinite scalability

---

## 📁 Epic Tech Stack Files

```
docs/
├── epic-1-tech-stack.md          (Setup & Scaffolding)
├── epic-2-tech-stack.md          (Translation Pipeline)
├── epic-3-tech-stack.md          (UI Polish)
├── epic-4-tech-stack.md          (Launch Prep)
└── EPIC-TECH-STACK-SUMMARY.md    (This file)

Supporting Files:
├── architecture.md                (System design)
├── sprint-plan.md                 (Timeline)
├── sprint-status.yaml             (Progress tracking)
├── SPRINT-OVERVIEW.md             (Sprint guide)
└── sprint-artifacts/              (Individual stories)
    ├── 1-1-project-initialization.md
    ├── 1-2-database-infrastructure.md
    ├── ... (all 20 stories)
    └── 4-5-beta-launch.md
```

---

## 🚀 Next Steps

1. ✅ All epic tech stacks created and documented
2. ✅ Sprint-status.yaml updated to reflect contexted epics
3. 📋 Ready to begin Story 1.2 (Database & Infrastructure)
4. 📋 Ready to create story context files for detailed implementation

---

**Status:** ✅ All 4 Epics Contexted

All technologies documented, dependencies identified, and integration points mapped.
TransKeep is ready for development!

**Created:** November 15, 2025  
**Last Updated:** November 15, 2025  
**Coverage:** 100% (4/4 epics, 20/20 stories)
