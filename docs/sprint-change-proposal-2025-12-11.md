# Sprint Change Proposal: PDF Reconstruction & S3 Upload

**Date:** December 11, 2025  
**Author:** Amelia (Developer Agent)  
**Status:** Pending Implementation  
**Priority:** CRITICAL (Blocks Epics 3 & 4)

---

## 1. Issue Summary

### Problem Statement

The translation pipeline successfully completes extraction and translation phases but **lacks the critical final step**: reconstructing the translated PDF and uploading it to S3. This renders the entire pipeline incomplete—users cannot download their translated documents.

### Discovery Context

During code review of the translation workflow, the following gaps were identified:

1. **`/backend/app/tasks/translate_blocks.py`** completes translation and caches results in Redis but does NOT generate a PDF
2. **`/backend/app/tasks/orchestrator.py`** chains extract → translate but has no reconstruction step
3. **`/backend/app/routers/translation.py`** download endpoint expects result PDF at S3 path but file is never created
4. **Epic 2 tech stack documentation** (line 202-209) explicitly documents "RECONSTRUCT PDF" as Step 5 but is unimplemented

### Evidence & Impact

- Download endpoint returns 404 for translated PDF files
- Users can view translations in UI but cannot retrieve final document
- Entire Epic 2 success criteria unfulfilled
- Epics 3 (UI Polish) and 4 (Launch) are blocked waiting for working end-to-end pipeline

---

## 2. Impact Analysis

### Epic Impact Assessment

#### **Epic 2: Core Translation Pipeline (Current)**
- **Status:** INCOMPLETE - Missing final reconstruction step
- **Affected Stories:** All 2.1-2.5 (pipeline incomplete without step 5)
- **Required Change:** Add Story 2.6 (PDF Reconstruction & S3 Upload)
- **Timeline Impact:** +1 day (extends Dec 9-13 to Dec 9-14)

#### **Epic 3: UI Polish & Refinement (Blocked)**
- **Status:** BLOCKED on Epic 2 completion
- **Affected Stories:** Story 3.4 (PDF Download with Edits)
- **Dependency:** Requires reconstructed PDF to exist in S3
- **Timeline Impact:** Cannot start until Epic 2 complete

#### **Epic 4: Launch Prep & Beta (Blocked)**
- **Status:** BLOCKED on Epics 2 & 3
- **Dependency:** End-to-end pipeline must be working before production deployment
- **Timeline Impact:** Prevents launch timeline

### Artifact Conflicts

#### **PRD Alignment** ✅ No conflicts
The PRD goal of "translate PDFs while preserving format" requires this reconstruction step. This change fulfills the original vision.

#### **Architecture** ✅ No conflicts
Architecture supports this work:
- PyMuPDF already used in extraction (Story 2.2)
- S3 infrastructure in place
- Celery orchestration framework ready
- Redis caching operational

#### **Technology Stack** ✅ All technologies proven
- PyMuPDF 1.23+ (already in use)
- boto3 (already in use)
- Celery (already in use)
- S3/MinIO (already in use)

---

## 3. Recommended Approach

### Selected Path: Direct Adjustment (Option 1)

**Rationale:**
- Issue is a missing implementation piece, not a design problem
- All required technologies already proven in project
- Clean scope: one new story fitting logically into existing epic
- Minimal risk: reuses established patterns
- Timeline: Adds only 1 day to Epic 2

### Implementation Strategy

**Scope Classification:** MINOR
- One new story (2.6) within existing epic framework
- Reuses proven technologies (PyMuPDF, S3, Celery)
- Directly addresses gap in documented pipeline
- No dependency rework needed

**Timeline Impact:**
- Original Epic 2: Dec 9-13 (5 days)
- Updated Epic 2: Dec 9-14 (6 days, +1 day)
- Epic 3 start: Dec 15 (unchanged relative sequence)
- Epic 4 start: Dec 22 (2 days earlier than planned Dec 23-27, now Dec 22-26)

**Risk Assessment:** LOW
- Technology proven in Story 2.2 (PDF extraction)
- Clear acceptance criteria defined
- Straightforward orchestration addition
- No API/schema changes needed

---

## 4. Detailed Change Proposals

### Change 1: Add Story 2.6 to Epic 2

**Document:** Epic 2 Stories Definition  
**Type:** New Story Addition  
**Scope:** Extends Epic 2 from Stories 2.1-2.5 to 2.1-2.6

```markdown
### Story 2.6: PDF Reconstruction & S3 Upload

**Epic:** 2  
**Title:** Reconstruct translated PDF and upload to S3  
**Duration:** 1 day (Est. 6-8 hours development + testing)  
**Dependency:** Requires Story 2.3 (Translation) complete  
**Priority:** CRITICAL (Blocks Epics 3 & 4)

#### Acceptance Criteria

1. **Celery Task Implementation**
   - Async task `reconstruct_pdf_task()` in `/backend/app/tasks/reconstruct_pdf.py`
   - Takes job_id as input
   - Max timeout: 15 minutes (supports 500+ page PDFs)
   - Retry on transient failures: max 3 attempts with exponential backoff

2. **PDF Reconstruction Logic**
   - Load original PDF from S3 (cached locally during processing)
   - Load translated blocks from Redis cache
   - Handle tone-customized translations if present (uses tone_customized_text over translated_text)
   - Use PyMuPDF to reconstruct PDF:
     - Replace text while preserving coordinates
     - Maintain original fonts, font sizes, styles
     - Preserve page layout and formatting
   - Works for PDFs: 1 page to 500+ pages
   - Processing time: <30 seconds for 100-page PDF

3. **S3 Upload**
   - Upload reconstructed PDF to S3 at path: `results/{user_id}/{job_id}/{filename}`
   - Use `S3Keys.result_path()` helper for consistent paths
   - Content-Type: `application/pdf`
   - Store path in Database: `Translation.translated_pdf_path`

4. **Database Updates**
   - Update Translation record:
     - Set `translated_pdf_path` to S3 key
     - Update `status` → `completed`
   - Maintain audit trail with timestamps

5. **Error Handling**
   - If S3 upload fails: retry 3 times, then mark job `failed`
   - If reconstruction fails: mark job `failed`, log error message
   - Store error in `Translation.error_message`
   - Publish error event for monitoring

6. **Integration with Pipeline**
   - Part of Celery task chain: extract → translate → reconstruct
   - Called from `orchestrator.process_translation_pipeline()`
   - Updates pipeline status tracking
   - Completes translation job

#### Technical Notes

**Implementation Files:**
- `backend/app/tasks/reconstruct_pdf.py` - Main task definition
- `backend/app/services/pdf_reconstruction.py` - PyMuPDF logic
- `backend/tests/test_pdf_reconstruction.py` - Unit & integration tests

**Dependencies:**
- PyMuPDF (fitz) 1.23+ (already in requirements)
- boto3 (already in requirements)
- Celery (already configured)

**Data Flow:**
```
Original PDF (S3)
    ↓
PyMuPDF loads & reads
    ↓
Translated blocks (Redis cache)
    ↓
Text replacement (preserve coords/fonts)
    ↓
Reconstructed PDF (bytes)
    ↓
Upload to S3
    ↓
Update Translation.translated_pdf_path
```

#### Testing Strategy

- **Unit Tests:**
  - PyMuPDF text replacement with various PDF structures
  - Coordinate preservation for different font sizes
  - Tone customization path selection logic

- **Integration Tests:**
  - Full pipeline: upload → extract → translate → reconstruct → download
  - Error scenarios: S3 upload timeout, malformed PDF
  - Large PDFs: 1, 10, 100, 500+ page documents

- **Manual Testing:**
  - Visual inspection of reconstructed PDFs
  - Text accuracy verification
  - Font/style preservation verification
```

---

### Change 2: Update Epic 2 Tech Stack Documentation

**Document:** `/docs/epic-2-tech-stack.md`  
**Type:** Documentation Update  
**Changes:**

1. **Line 2:** Update Overview to include "PDF reconstruction with S3 upload"
2. **Line 6:** Update Stories count from 2.1-2.5 to 2.1-2.6
3. **Line 6:** Update Duration from "5 days" to "6 days" (Dec 9-14)
4. **After line 143:** Add Story 2.6 tech stack mapping section
5. **Line 202-209:** Update Data Flow section to mark reconstruction as Story 2.6

**Rationale:** 
- Reflects new story in epic scope
- Makes reconstruction explicit in architecture documentation
- Clarifies data dependencies for reconstruction step

---

### Change 3: Update Pipeline Orchestrator

**Document:** `/backend/app/tasks/orchestrator.py`  
**Type:** Code Update  
**Changes:**

**Location:** Line 112 (after translation step)

Add reconstruction step to pipeline:

```python
# Step 3: Reconstruct PDF with translations
info("Pipeline step 3: Reconstructing PDF", job_id=job_id)
from app.tasks.reconstruct_pdf import reconstruct_pdf_sync

reconstruction_result = await reconstruct_pdf_sync(job_id, db)

if not reconstruction_result["success"]:
    raise Exception(f"Reconstruction failed: {reconstruction_result.get('error', 'Unknown error')}")
```

**Location:** Line 126 (return statement)

Update return object to include reconstruction result:

```python
return {
    "success": True,
    "job_id": job_id,
    "extraction": extraction_result,
    "translation": translation_result,
    "reconstruction": reconstruction_result,  # NEW
}
```

**Rationale:**
- Integrates Story 2.6 into pipeline execution flow
- Maintains sequential execution: extract → translate → reconstruct
- Provides logging and result capture for monitoring
- Ensures pipeline fails if reconstruction fails

---

## 5. Implementation Handoff

### Change Scope Classification

**MINOR** - Can be implemented directly by development team

- One self-contained story
- Reuses proven technologies
- No cross-team dependencies
- No API/schema changes

### Handoff Recipients

**Primary:** Development Team (Roy)  
**Responsibility:** Implement Story 2.6 and update related files

**Timeline:**
- **Dec 12-13:** Story 2.6 implementation and testing
- **Dec 14:** Integration testing with full pipeline
- **Dec 14 EOD:** Epic 2 complete, ready for Epic 3 start

### Success Criteria for Implementation

1. ✅ Story 2.6 implementation complete with all ACs satisfied
2. ✅ PDF reconstruction works for 1, 10, 100, 500+ page PDFs
3. ✅ Translated PDFs appear in S3 at correct paths
4. ✅ Download endpoint successfully serves reconstructed PDFs
5. ✅ All tests passing (unit + integration)
6. ✅ Pipeline orchestration complete: extract → translate → reconstruct
7. ✅ Error handling working: S3 upload retries, job failure marking
8. ✅ Documentation updated in epic-2-tech-stack.md
9. ✅ No data loss or corruption in PDF reconstruction
10. ✅ Performance verified: reconstruction <30 sec for 100 pages

### Next Steps After Implementation

1. **Upon Epic 2 Completion:**
   - Unblock Epic 3 (UI Polish & Refinement)
   - Story 3.4 can now proceed with PDF download feature

2. **Upon Epic 3 Completion:**
   - Unblock Epic 4 (Launch Prep & Beta)
   - Ready for production deployment

---

## 6. Appendix: Change Proposal Summary

| Item | Details |
|------|---------|
| **Issue** | Missing PDF reconstruction and S3 upload in translation pipeline |
| **Root Cause** | Story 2.6 not implemented (documented but unbuilt) |
| **Impact Scope** | Epic 2 (current), Epic 3 (blocked), Epic 4 (blocked) |
| **Change Type** | Feature Addition (1 new story) |
| **Scope Classification** | MINOR |
| **Timeline Impact** | +1 day to Epic 2 (Dec 9-14), no change to Epics 3-4 relative start |
| **Risk Level** | LOW (proven technology, clear scope) |
| **Dependencies** | None (self-contained) |
| **Cross-team Coordination** | None required |
| **Effort Estimate** | 6-8 hours development, 2-4 hours testing |
| **Handoff To** | Development Team |

---

**Document Status:** PENDING USER APPROVAL  
**Generated:** December 11, 2025 by Amelia (Developer Agent)
