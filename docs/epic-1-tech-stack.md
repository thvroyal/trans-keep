# Epic 1: Setup & Scaffolding - Tech Stack & Architecture

**Epic:** 1  
**Title:** Setup & Scaffolding 🏗️  
**Stories:** 1.1 - 1.5  
**Duration:** 5 days (Dec 2-6)  
**Status:** contexted  
**Created:** November 15, 2025

---

## Overview

Establish the complete development environment with all frameworks initialized, deployment pipelines ready, and monitoring configured. This epic lays the foundation for all subsequent development.

---

## 📦 Tech Stack by Component

### **Frontend Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Runtime** | Node.js | 20+ | Stable LTS, strong ecosystem | `node -v` check |
| **Framework** | React | 18 | Type-safe JSX, hooks, performance | `npm create vite` |
| **Language** | TypeScript | 5.x | Type safety, error prevention | Included with Vite |
| **Bundler** | Vite | 5.x | Lightning-fast HMR, ESM | Included with Vite |
| **Package Mgr** | npm | 10+ | Reliable, widely used | Default with Node |
| **Styling** | Tailwind CSS | 3.x | Utility-first, responsive | `npm install tailwindcss` |
| **Components** | shadcn/ui | Latest | Pre-built accessible components | `npx shadcn-ui@latest init` |
| **Routing** | React Router | 6.x | Client-side navigation | `npm install react-router-dom` |
| **State** | Zustand | Latest | Lightweight, simple API | `npm install zustand` |
| **Config** | vite.config.ts | - | Build optimization | Auto-generated |
| **TypeScript** | tsconfig.json | - | Type checking configuration | Auto-generated |

### **Backend Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Runtime** | Python | 3.11 | Rich ecosystem, type hints | System Python |
| **Package Mgr** | uv | Latest | 5-20x faster than pip, deterministic | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Framework** | FastAPI | 0.104+ | Async-first, auto-docs, type-safe | `uv pip install fastapi` |
| **Server** | Uvicorn | 0.24+ | ASGI server, production-ready | `uv pip install uvicorn` |
| **Database ORM** | SQLAlchemy | 2.0+ | Type-safe queries, migrations | `uv pip install sqlalchemy` |
| **Migrations** | Alembic | 1.12+ | Database version control | `uv pip install alembic` |
| **Validation** | Pydantic | 2.5+ | Data validation, serialization | Auto-dependency of FastAPI |
| **Settings** | pydantic-settings | 2.1+ | Environment configuration | `uv pip install pydantic-settings` |
| **Async Support** | anyio | 4.x | Async utilities | Auto-dependency |
| **Config** | pyproject.toml | - | Project metadata and dependencies | Manual creation |

### **Database Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Primary DB** | PostgreSQL | 15 | Reliable ACID, JSON support, full-text search | Docker image: `postgres:15-alpine` |
| **Connection** | psycopg2-binary | 2.9+ | PostgreSQL adapter for Python | `uv pip install psycopg2-binary` |
| **Connection Pool** | SQLAlchemy Pool | Built-in | Manage connections efficiently | Part of SQLAlchemy |
| **Local Dev** | Docker Postgres | 15-alpine | Lightweight container, same as production | Docker Compose service |
| **Prod DB** | AWS RDS | PostgreSQL 15 | Managed service, automated backups | AWS Console provisioning |

### **Cache & Queue Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Cache** | Redis | 7 | Fast in-memory store, Celery broker | Docker image: `redis:7-alpine` |
| **Python Client** | redis-py | 5.0+ | Redis operations from Python | `uv pip install redis` |
| **Async Client** | aioredis | 2.0+ | Async Redis operations | `uv pip install aioredis` |
| **Task Queue** | Celery | 5.3+ | Distributed task processing | `uv pip install celery` |
| **Prod Cache** | AWS ElastiCache | Redis 7 | Managed Redis cluster | AWS Console provisioning |

### **Authentication Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Auth Library** | better-auth | Latest | OAuth + JWT, framework-agnostic | Backend: `pip install better-auth` |
| **Frontend Hooks** | @better-auth/react | Latest | React integration | Frontend: `npm install @better-auth/react` |
| **Provider** | Google OAuth | - | User authentication | Google Cloud Console setup |
| **Tokens** | JWT | - | Stateless authentication | Built into better-auth |
| **Session** | httpOnly Cookies | - | Secure token storage | Browser security feature |

### **Observability Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Tracing** | OpenTelemetry API | 1.21+ | Vendor-neutral observability | `uv pip install opentelemetry-api` |
| **SDK** | OpenTelemetry SDK | 1.21+ | Core instrumentation | `uv pip install opentelemetry-sdk` |
| **FastAPI Instr.** | otel-instrumentation-fastapi | 0.42b0+ | Auto-trace FastAPI endpoints | `uv pip install opentelemetry-instrumentation-fastapi` |
| **Jaeger Export** | opentelemetry-exporter-jaeger | 1.21+ | Send traces to Jaeger | `uv pip install opentelemetry-exporter-jaeger` |
| **Trace Viz** | Jaeger UI | Latest | Visualize distributed traces | Docker image: `jaegertracing/all-in-one:latest` |
| **Logs** | Structured JSON | - | Machine-readable logs | Custom logging utilities |
| **Prod Obs** | AWS CloudWatch | - | Production observability | AWS console integration |

### **Infrastructure Stack**

| Component | Technology | Version | Why | Installation |
|-----------|------------|---------|-----|--------------|
| **Containerization** | Docker | 24+ | Consistent environments | System Docker install |
| **Orchestration** | Docker Compose | 2.x | Multi-service local dev | Part of Docker Desktop |
| **CI/CD** | GitHub Actions | - | Native GitHub integration | `.github/workflows/` YAML files |
| **Frontend Build** | Vite Build | - | Production bundle generation | `npm run build` command |
| **Backend Build** | Docker Build | - | Backend container image | `docker build` command |
| **Prod Frontend** | AWS S3 + CloudFront | - | Static file hosting + CDN | AWS provisioning |
| **Prod Backend** | AWS ECS | - | Container orchestration | AWS provisioning |
| **Prod DB** | AWS RDS | - | Managed PostgreSQL | AWS provisioning |
| **Prod Cache** | AWS ElastiCache | - | Managed Redis | AWS provisioning |

---

## 🔧 Epic 1 Stories & Tech Usage

### **Story 1.1: Project Initialization**
- **Frontend:** React 18, TypeScript, Vite, npm
- **Backend:** FastAPI, Python 3.11, uv
- **Infrastructure:** Docker, Docker Compose, GitHub Actions
- **Output:** Two repos (frontend, backend) ready for development

### **Story 1.2: Database & Infrastructure Setup**
- **Database:** PostgreSQL 15, Alembic, SQLAlchemy
- **Cache:** Redis 7, redis-py
- **Storage:** AWS S3 / MinIO
- **Migration:** Alembic version control
- **Output:** Database schema, Redis connection, S3 buckets

### **Story 1.3: Google OAuth Integration**
- **Auth:** better-auth library, Google OAuth 2.0
- **Backend:** JWT token generation and validation
- **Frontend:** @better-auth/react hooks
- **Security:** httpOnly cookies, CORS configuration
- **Output:** Sign-in/sign-out working, user sessions established

### **Story 1.4: Frontend Scaffold & shadcn/ui Setup**
- **Components:** React 18, shadcn/ui, Tailwind CSS
- **Routing:** React Router v6
- **State:** Zustand store
- **Styling:** Tailwind CSS with custom palette
- **Output:** Multi-page app with proper structure

### **Story 1.5: OpenTelemetry & Monitoring Setup**
- **Tracing:** OpenTelemetry API + SDK
- **Backend:** FastAPI instrumentation
- **Frontend:** Web SDK instrumentation
- **Visualization:** Jaeger UI
- **Output:** Traces flowing to Jaeger, logs structured

---

## 📊 Dependencies & Integration Points

### **Frontend Dependencies**

```
node_modules/
├── react                      # Core framework
├── react-dom                  # DOM rendering
├── typescript                 # Type checking
├── vite                       # Bundler
├── tailwindcss               # Styling
├── shadcn-ui                 # Component library
├── react-router-dom          # Routing
├── zustand                   # State management
├── @opentelemetry/api        # Tracing
└── @better-auth/react        # Authentication hooks
```

### **Backend Dependencies**

```
site-packages/
├── fastapi                   # Web framework
├── uvicorn                   # ASGI server
├── sqlalchemy                # ORM
├── alembic                   # Migrations
├── psycopg2-binary          # PostgreSQL adapter
├── redis                     # Redis client
├── aioredis                  # Async Redis
├── celery                    # Task queue
├── pydantic                  # Validation
├── opentelemetry-*          # Observability
└── better-auth              # Authentication
```

### **Environment Integration**

```
Docker Compose Services:
├── frontend (Node 20, port 5173 → 3000)
├── backend (Python 3.11, port 8000)
├── postgres (PostgreSQL 15, port 5432)
├── redis (Redis 7, port 6379)
└── jaeger (Jaeger UI, port 16686)
```

---

## 🚀 Deployment Architecture

### **Local Development (Docker Compose)**
```
docker-compose.yml
├── Frontend service (npm run dev)
├── Backend service (uvicorn + reload)
├── PostgreSQL (local data)
├── Redis (local cache)
└── Jaeger (local tracing)
```

### **Production (AWS)**
```
AWS Stack:
├── Frontend: CloudFront + S3
├── Backend: ECS (Fargate)
├── Database: RDS PostgreSQL
├── Cache: ElastiCache Redis
├── Observability: CloudWatch
└── CDN: CloudFront edge locations
```

---

## 📋 Installation Checklist for Epic 1

### **System Requirements**
- [ ] Node.js 20+ installed (`node -v`)
- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] uv installed (`uv --version`)
- [ ] Docker installed (`docker --version`)
- [ ] Docker Compose installed (`docker-compose --version`)
- [ ] Git installed (`git --version`)

### **Frontend Setup (Story 1.1)**
- [ ] `npm create vite@latest frontend --template react-ts`
- [ ] `cd frontend && npm install`
- [ ] Create `vite.config.ts`
- [ ] Create `tailwind.config.ts`
- [ ] Create `.env.local`

### **Backend Setup (Story 1.1)**
- [ ] `mkdir backend && cd backend`
- [ ] Create `pyproject.toml` with dependencies
- [ ] `uv venv` (create virtual environment)
- [ ] `uv pip install -e .` (install dependencies)
- [ ] Create `app/main.py`
- [ ] Create `.env`

### **Database Setup (Story 1.2)**
- [ ] `alembic init migrations`
- [ ] Create SQLAlchemy models
- [ ] Create initial migration: `alembic revision --autogenerate`
- [ ] Test migration: `alembic upgrade head`
- [ ] Verify database connection

### **Authentication Setup (Story 1.3)**
- [ ] Register Google OAuth app (Google Cloud Console)
- [ ] Store CLIENT_ID and CLIENT_SECRET in `.env`
- [ ] Configure redirect URIs
- [ ] Install `better-auth` (backend and frontend)
- [ ] Implement OAuth endpoints
- [ ] Test sign-in flow

### **Frontend Framework Setup (Story 1.4)**
- [ ] Install React Router: `npm install react-router-dom`
- [ ] Install Zustand: `npm install zustand`
- [ ] Install shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Add UI components needed
- [ ] Create page components (Upload, Processing, Review)
- [ ] Configure routing

### **Observability Setup (Story 1.5)**
- [ ] Install OpenTelemetry packages
- [ ] Configure Jaeger exporter
- [ ] Add FastAPI instrumentation
- [ ] Add frontend tracing
- [ ] Verify Jaeger UI at localhost:16686

---

## 🎯 Success Criteria for Epic 1

**All stories in Epic 1 must satisfy:**

- ✅ `docker-compose up --build` successfully starts all services
- ✅ All services are healthy (health checks passing)
- ✅ Frontend loads at http://localhost:3000
- ✅ Backend API accessible at http://localhost:8000
- ✅ Swagger UI available at http://localhost:8000/docs
- ✅ Database migrations run automatically
- ✅ Can sign in with Google (OAuth working)
- ✅ User sessions persist across page reloads
- ✅ Traces visible in Jaeger UI (http://localhost:16686)
- ✅ All logs include trace context
- ✅ CI/CD pipelines execute on push
- ✅ No console errors or warnings (except intentional)
- ✅ TypeScript strict mode enabled and passing
- ✅ All dependencies locked (requirements.txt, package-lock.json)

---

## 📚 Key Documentation Files

- **Architecture:** `docs/architecture.md`
- **Sprint Plan:** `docs/sprint-plan.md`
- **uv Setup Guide:** `docs/uv-setup-guide.md`
- **Environment Variables:** `.env.example` files
- **Tech Stack Summary:** `docs/tech-decisions-summary.txt`

---

## 🔗 External Resources

### **Frontend**
- [React 18 Docs](https://react.dev)
- [Vite Guide](https://vitejs.dev)
- [TypeScript Handbook](https://www.typescriptlang.org)
- [shadcn/ui](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
- [React Router](https://reactrouter.com)
- [Zustand](https://github.com/pmndrs/zustand)

### **Backend**
- [FastAPI](https://fastapi.tiangolo.com)
- [SQLAlchemy](https://docs.sqlalchemy.org)
- [Alembic](https://alembic.sqlalchemy.org)
- [Pydantic](https://docs.pydantic.dev)
- [uv Package Manager](https://docs.astral.sh/uv/)

### **Infrastructure**
- [Docker](https://docs.docker.com)
- [Docker Compose](https://docs.docker.com/compose)
- [GitHub Actions](https://docs.github.com/en/actions)
- [OpenTelemetry](https://opentelemetry.io)
- [Jaeger](https://www.jaegertracing.io)

---

## 📝 Notes

- **Python Version:** Locked to 3.11 for compatibility with all dependencies
- **Package Manager:** uv provides 5-20x faster installations and deterministic builds
- **Docker:** Multi-stage builds optimize image size and startup time
- **Tracing:** OpenTelemetry protocol allows switching backends (CloudWatch, Datadog, etc.) without code changes
- **CORS:** Configure based on frontend URL (localhost:3000 in dev, production URL in prod)
- **Environment:** All secrets must be in `.env` files (not committed to git)

---

**Epic 1 Tech Stack Status:** ✅ **CONTEXTED**

All technologies identified, versions pinned, and installation paths documented.
Ready for Stories 1.1-1.5 implementation.

**Created:** November 15, 2025  
**Last Updated:** November 15, 2025

