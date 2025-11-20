# Tech Refinements - November 14, 2025

**Updated by:** Roy  
**Changes Made:** 3 critical technical decisions refined  

---

## 1. Logging: OpenTelemetry (Otel) Protocol ✅

**Change:** Replace CloudWatch direct logging with OpenTelemetry standard

**Why:**
- Vendor-agnostic (can switch from CloudWatch to Datadog/Jaeger without code changes)
- Industry standard for observability (logging + tracing + metrics)
- Better distributed tracing (trace_id/span_id across services)
- Future-proof

**What to implement:**
- Backend: `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp`
- Workers: `opentelemetry-instrumentation-celery`
- Frontend: `@opentelemetry/api` + HTTP exporter
- Deploy Otel Collector in ECS to receive traces and forward to CloudWatch

**Phase 1 Setup:**
- Local development: Export to Jaeger (UI at localhost:16686)
- Production: Export to CloudWatch Logs + X-Ray

**Impact on timeline:** +1-2 hours setup, minimal impact on development

---

## 2. OAuth: better-auth instead of NextAuth ✅

**Change:** Use `better-auth` library (lighter, framework-agnostic)

**Why:**
- Works with ANY backend (not just Next.js)
- Better FastAPI integration
- Simpler API surface
- Smaller bundle size (frontend)
- Easier to understand/maintain

**What to implement:**
- Backend: `pip install better-auth` + Google provider setup
- Frontend: `npm install @better-auth/react`
- Flow: Google consent → OAuth code exchange → JWT token in httpOnly cookie

**Code already drafted in architecture.md (Section 2.3)**

**Impact on timeline:** -30 min (simpler than NextAuth)

---

## 3. PDF Editing Flow: In-Memory + Rebuild on Download ✅

**Change:** When user edits a PDF block, track edits in frontend state. Rebuild PDF only when downloading.

**Why this approach (Option A):**
- ✅ **MVP speed:** No complex PDF manipulation during session
- ✅ **Performance:** Instant feedback (just update React state)
- ✅ **Cost:** $0 additional overhead
- ✅ **Simplicity:** Zustand store + send edits with download request
- ❌ Edits lost if user closes browser (acceptable for MVP)

**What NOT to do:**
- ❌ Option B (Rebuild individual blocks): Too complex for MVP
- ❌ Option C (Full PDF rebuild on each edit): Way too slow

**Implementation:**

Frontend (Zustand):
```typescript
edits: Map<block_id, new_text>
editBlock(blockId, newText) {
  this.edits.set(blockId, newText)  // Instant UI update
}
```

Backend (FastAPI):
```python
@router.get("/download/{job_id}")
async def download(job_id: str, edits: List[Tuple]):
    translated = load_from_s3(job_id)
    for block_id, new_text in edits:
        translated[block_id]["text"] = new_text
    return reconstruct_pdf(translated)  # 5-15 sec
```

**User Experience:**
- Edit feedback: ⚡ Instant
- Download: ~10 seconds (rebuild with edits)
- No UI jank or delays during editing

**Phase 2 Optimization:**
- If editing becomes bottleneck, switch to Option B (rebuild just blocks)
- Or implement HTML rendering (edit in HTML → export to PDF)

**Impact on timeline:** MVP is actually FASTER with this approach (less complex)

---

## Summary of Changes

| Item | Original | Updated | Impact |
|------|----------|---------|--------|
| **Logging** | CloudWatch direct | OpenTelemetry | +1-2 hrs setup, better observability |
| **OAuth** | NextAuth | better-auth | -30 min, simpler code |
| **PDF Editing** | Unclear | In-Memory tracking | Faster MVP, simpler, instant feedback |

---

## Action Items for Development Team

1. **Week 1 Setup:**
   - [ ] Install Otel packages (backend + frontend)
   - [ ] Configure better-auth with Google provider
   - [ ] Set up Zustand store for edit tracking

2. **Week 2-3 Implementation:**
   - [ ] Implement Otel tracing throughout backend
   - [ ] Implement better-auth OAuth flow
   - [ ] Implement edit tracking in ReviewPanel

3. **Infrastructure:**
   - [ ] Deploy Otel Collector in ECS
   - [ ] Configure CloudWatch metrics + alarms

---

## All Three Changes Finalized ✅

Architecture document updated with all refinements. Ready to hand off to development!

**Next:** Approve these changes, then proceed to Sprint Planning (Week 1-4 breakdown).

