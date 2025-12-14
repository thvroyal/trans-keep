# 12. Architecture Decisions Reference

## Decision Records

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
