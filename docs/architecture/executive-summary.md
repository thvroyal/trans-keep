# Executive Summary

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
