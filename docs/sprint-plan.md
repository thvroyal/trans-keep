# TransKeep - 4-Week Sprint Plan

**Created:** November 14, 2025  
**Project:** TransKeep MVP  
**Timeline:** 1 month to launch  
**Team:** 1-2 developers  

---

## Executive Summary

**Goal:** Launch MVP with core translation flow + review interface + tone customization

**Timeline:** 4 weeks (Week 1-4)

**Delivery:** 
- Week 1: Setup & Scaffolding ✅ Foundation ready
- Week 2: Core Pipeline ✅ Translation working
- Week 3: UI Polish ✅ Review experience perfect
- Week 4: Launch ✅ Beta to 50 users

---

## Week 1: Setup & Scaffolding 🏗️

**Duration:** 5 days (Dec 2-6)  
**Owner:** Lead Developer  
**Goal:** Development environment ready, all frameworks initialized, auth working

### Story 1.1: Project Initialization
- [ ] Create frontend repo (React 18 + TypeScript + Vite)
- [ ] Create backend repo (FastAPI + Python 3.11 + uv)
- [ ] Create Docker Compose for local dev
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Initialize `pyproject.toml` with `uv pip install` dependencies
- **Time:** 1 day
- **Resources:** `pnpm create vite` + FastAPI scaffold + `uv` package manager

### Story 1.2: Database & Infrastructure Setup
- [ ] PostgreSQL schema creation (users, translations tables)
- [ ] Redis setup for Celery
- [ ] S3 bucket creation (local + AWS)
- [ ] Environment variables (.env setup)
- [ ] Database migrations (Alembic)
- **Time:** 1 day
- **Resources:** Docker Compose, Alembic, AWS console

### Story 1.3: Google OAuth Integration
- [ ] Register Google OAuth app (get client ID/secret)
- [ ] Backend: better-auth setup with Google provider
- [ ] Frontend: better-auth React wrapper
- [ ] Test sign-in/sign-out flow locally
- **Time:** 1 day
- **Resources:** better-auth docs, Google Cloud Console

### Story 1.4: Frontend Scaffold & shadcn/ui Setup
- [ ] Install shadcn/ui components
- [ ] Create project layout (Upload page, Processing page, Review page)
- [ ] Set up React Router
- [ ] Set up Zustand store (basic)
- [ ] Set up Tailwind + TransKeep color palette
- **Time:** 1 day
- **Resources:** shadcn/ui CLI, Tailwind config

### Story 1.5: OpenTelemetry & Monitoring Setup
- [ ] Install Otel packages (backend + frontend)
- [ ] Configure Otel exporter to local Jaeger
- [ ] Add basic tracing to FastAPI endpoints
- [ ] Verify logs appear in Jaeger UI
- **Time:** 1 day
- **Resources:** Otel docs, Docker image for Jaeger

**Definition of Done:**
- ✅ `docker-compose up` starts all services
- ✅ Frontend loads at localhost:3000
- ✅ Backend docs at localhost:8000/docs
- ✅ Can sign in with Google
- ✅ Logs visible in Jaeger

---

## Week 2: Core Translation Pipeline 🔄

**Duration:** 5 days (Dec 9-13)  
**Owner:** Backend Developer  
**Goal:** Upload → Extract → Translate → Status polling working end-to-end

### Story 2.1: File Upload Endpoint
- [ ] POST /api/v1/upload endpoint (chunked uploads)
- [ ] Validate file type (PDF only)
- [ ] Validate file size (max 100MB)
- [ ] Store to S3 temporarily
- [ ] Create translation record in DB
- [ ] Return job_id to client
- **Time:** 1.5 days
- **Resources:** FastAPI multipart uploads, boto3 (S3), Pydantic validation

### Story 2.2: PDF Extraction with PyMuPDF
- [ ] Implement extract_text_with_layout() function
- [ ] Extract text blocks + coordinates + page info
- [ ] Store extracted data in Redis (cache)
- [ ] Handle scanned PDFs (detect → plan for Phase 2)
- [ ] Test with 10, 100, 500 page PDFs
- **Time:** 1.5 days
- **Resources:** PyMuPDF (fitz), performance testing

### Story 2.3: DeepL Translation Integration
- [ ] Set up DeepL API client
- [ ] Implement batch translation (10 blocks per request)
- [ ] Implement parallelization (pages in parallel)
- [ ] Handle errors and retries
- [ ] Test cost ($0.15 per 100k words budget)
- **Time:** 1.5 days
- **Resources:** DeepL Python client, Celery async

### Story 2.4: Celery Job Queue Setup
- [ ] Create Celery app with Redis broker
- [ ] Implement extract_and_translate task
- [ ] Task orchestration (extract → translate → tone → reconstruct)
- [ ] Error handling and retry logic
- [ ] Monitor job status via logs
- **Time:** 1.5 days
- **Resources:** Celery docs, Redis

### Story 2.5: Status Polling Endpoint
- [ ] GET /api/v1/status/{job_id} endpoint
- [ ] Return: status, progress %, page count, ETA
- [ ] Frontend polling (every 2 seconds)
- [ ] Show progress UI on Processing page
- [ ] Test with long-running jobs
- **Time:** 1 day
- **Resources:** TanStack Query (useQuery with refetchInterval)

**Definition of Done:**
- ✅ Upload PDF → See "Processing..." with progress
- ✅ Job completes → Status changes to "Complete"
- ✅ No errors for 10, 100, 500 page PDFs
- ✅ Stays within DeepL budget
- ✅ Logs visible in Jaeger with trace IDs

---

## Week 3: UI Polish & Refinement ✨

**Duration:** 5 days (Dec 16-20)  
**Owners:** Frontend Developer + Backend Developer  
**Goal:** Review experience perfect, edits working, download ready

### Story 3.1: Side-by-Side Review Panel (Hero Component)
- [ ] Implement dual PDF rendering (pdf.js)
- [ ] Synchronized scrolling (default ON, toggle OFF)
- [ ] Hover highlighting (block-level mapping)
- [ ] Responsive design (desktop → tablet → mobile tabs)
- [ ] Performance optimization (large PDFs)
- **Time:** 2 days
- **Resources:** pdf.js, Zustand for scroll state, React hooks

### Story 3.2: Tone Customization UI & Logic
- [ ] Build ToneSelector component (5 presets + custom input)
- [ ] Integrate Claude Haiku for tone re-translation
- [ ] Visual feedback when tone applied
- [ ] Show before/after translations
- [ ] Test cost (~$0.048 per document)
- **Time:** 1.5 days
- **Resources:** Claude API, Anthropic Python client

### Story 3.3: Edit & Alternatives Workflow
- [ ] Implement EditPanel component (click-to-edit)
- [ ] Show 2-3 alternatives (from Claude)
- [ ] In-memory edit tracking (Zustand)
- [ ] Real-time preview in ReviewPanel
- [ ] Re-translate with custom tone (mini-workflow)
- **Time:** 1.5 days
- **Resources:** Zustand store, Anthropic API

### Story 3.4: PDF Download Endpoint
- [ ] GET /api/v1/download/{job_id} endpoint
- [ ] Apply edits from frontend (reconstruct with edits)
- [ ] Generate final PDF
- [ ] Pre-signed S3 URL for download
- [ ] Browser downloads directly from CloudFront
- **Time:** 1 day
- **Resources:** PDFBox or Chromium rendering, boto3

### Story 3.5: Error Handling & Edge Cases
- [ ] Network error recovery (retry with backoff)
- [ ] Large file handling (chunked uploads)
- [ ] Scanned PDF detection (warn user)
- [ ] Translation API failures (fallback to Google)
- [ ] User-friendly error messages
- **Time:** 1 day
- **Resources:** Error boundaries, error handling utilities

**Definition of Done:**
- ✅ Upload → See side-by-side review (no manual comparison needed)
- ✅ Hover highlighting works smoothly
- ✅ Tone presets apply instantly
- ✅ Edit/alternatives work perfectly
- ✅ Download creates clean PDF with edits
- ✅ No errors for typical usage

---

## Week 4: Launch Prep & Beta 🚀

**Duration:** 5 days (Dec 23-27)  
**Owners:** Entire team  
**Goal:** Deploy to AWS, final QA, launch to 50 beta users

### Story 4.1: Production Deployment
- [ ] Deploy to AWS ECS (backend)
- [ ] Deploy to CloudFront + S3 (frontend)
- [ ] Set up database (RDS PostgreSQL)
- [ ] Set up cache (ElastiCache Redis)
- [ ] Configure Otel Collector → CloudWatch
- [ ] DNS setup + SSL certificate
- **Time:** 1 day
- **Resources:** AWS CLI, CloudFormation (or manual setup)

### Story 4.2: Performance Optimization
- [ ] Load testing (200+ concurrent users)
- [ ] Optimize PDF extraction (check for bottlenecks)
- [ ] Optimize translation batching
- [ ] Database query optimization
- [ ] Frontend bundle optimization (Vite build)
- **Time:** 1.5 days
- **Resources:** k6 (load testing), profiling tools

### Story 4.3: Security Audit
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Multi-tenant isolation verified
- [ ] OAuth tokens properly validated
- [ ] File cleanup after 24 hours automated
- [ ] No sensitive data in logs
- **Time:** 0.5 days
- **Resources:** Manual review + automated security checks

### Story 4.4: Final QA & Bug Fixes
- [ ] End-to-end testing (upload → review → download)
- [ ] Cross-browser testing (Chrome, Safari, Firefox)
- [ ] Mobile responsiveness check
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Edge cases (large PDFs, slow internet, etc.)
- **Time:** 1 day
- **Resources:** Testing utilities, screen readers

### Story 4.5: Beta Launch
- [ ] Create launch announcement
- [ ] Set up beta user onboarding
- [ ] Monitor system health (Otel + CloudWatch)
- [ ] Prepare support/feedback process
- [ ] Launch to 50 users
- [ ] Daily standup for first week
- **Time:** 1 day
- **Resources:** Communication, monitoring

**Definition of Done:**
- ✅ Live at transkeep.com (or similar)
- ✅ 50 beta users accessing without errors
- ✅ Load testing passed (200+ concurrent)
- ✅ Security audit passed
- ✅ Performance acceptable (90s for 500 pages)
- ✅ Logs flowing to CloudWatch
- ✅ 24/7 monitoring in place

---

## Dependencies & Blockers

### Critical Path:
1. Week 1.3 (OAuth) must complete before Week 2 can start
2. Week 1.2 (DB) must complete before Week 2.1
3. Week 2.1, 2.2, 2.3 can run in parallel
4. Week 3.1 (ReviewPanel) should start after Week 2.5 (status polling)
5. Week 4.1 (Deployment) can start during Week 3

### External Dependencies:
- DeepL API key (available now)
- Claude API key (available now)
- Google OAuth credentials (setup takes 1 hour)
- AWS account (already set up)
- Better-auth library (production-ready)

---

## Team Capacity & Allocation

**Recommended Team:**
- 1 Backend Developer (Primary: backend API, Celery, PDF processing)
- 1 Frontend Developer (Primary: React UI, PDF rendering, state management)
- 1 DevOps/Infrastructure (Overlap: Weeks 1, 4)

**With 1 Developer (Solo):**
- Week 1: Setup (5 days)
- Week 2: Backend pipeline (5 days)
- Week 3: Frontend + edits (5-7 days)
- Week 4: Polish + launch (3-5 days)
- **Total:** 18-22 days (tight but doable with focus)

---

## Daily Standup Template

**Each day, report:**
- What did I complete yesterday?
- What am I working on today?
- Any blockers or issues?
- How much does it cost today? (Track DeepL + Claude)

---

## Success Criteria

**Week 1 Done:** All setup complete, auth working ✅  
**Week 2 Done:** Full pipeline working end-to-end ✅  
**Week 3 Done:** UI beautiful, all features working ✅  
**Week 4 Done:** Live in production, 50 users testing ✅  

**MVP Success:**
- ✅ 50+ users download translated documents in first month
- ✅ 70%+ users rate quality as good/excellent
- ✅ 60%+ of users use review feature
- ✅ No critical bugs blocking usage
- ✅ Processing time: 45-90 seconds for typical documents

---

## Post-Launch (Week 5+)

- Gather user feedback
- Fix critical bugs
- Plan Phase 2 (enterprise features, DOCX/PPTX)
- Scale infrastructure if needed

---

## Resources & Links

**Tech Stack Docs:**
- [React 18](https://react.dev)
- [FastAPI](https://fastapi.tiangolo.com)
- [better-auth](https://better-auth.com)
- [shadcn/ui](https://ui.shadcn.com)
- [PyMuPDF](https://pymupdf.readthedocs.io)
- [DeepL API](https://www.deepl.com/docs-api)
- [Claude API](https://anthropic.com/docs)
- [Celery](https://docs.celeryproject.io)

**Infrastructure:**
- AWS Console
- Docker Compose (local)
- Jaeger UI (monitoring)

---

**Status:** Ready to start Week 1 on Monday 🚀  
**Next:** Assign tasks to team members and begin!

