# Sprint Change Proposal: Replace PyMuPDF with PDFMathTranslate

**Date:** December 13, 2025  
**Author:** Roy  
**Change Type:** Technical Enhancement  
**Scope:** Epic 2 - Core Translation Pipeline  
**Status:** Draft for Review

---

## 1. Issue Summary

### Problem Statement

The current PyMuPDF-based PDF processing pipeline (implemented in Stories 2.2 and 2.6) may not preserve complex layouts (tables, equations, multi-column) as effectively as needed for technical documents. PDFMathTranslate offers AI-powered layout detection (DocLayout-YOLO) and is specifically designed for scientific/technical documents, providing superior format preservation.

### Context About Discovery

- **Trigger:** Need for better format preservation for technical documents
- **Discovery Method:** Research evaluation identified PDFMathTranslate as Option B with advantages for complex layouts
- **Evidence:**
  - PDFMathTranslate uses DocLayout-YOLO for precise layout detection
  - Specialized for scientific documents (tables, equations, multi-column layouts)
  - Open source and ready to use
  - Library is quickly available for integration

### Impact Demonstration

**Current Approach Limitations:**
- PyMuPDF extraction may miss complex table structures
- Multi-column layouts may not be preserved accurately
- Equations and mathematical formulas may lose formatting
- Technical documents with complex layouts require manual fixes

**PDFMathTranslate Advantages:**
- AI-powered layout detection (DocLayout-YOLO)
- Specialized for scientific/technical documents
- Better preservation of tables, equations, and complex layouts
- Open source with active development

---

## 2. Impact Analysis

### Epic Impact

**Epic 2: Core Translation Pipeline** - **MAJOR IMPACT**

**Affected Stories:**

1. **Story 2.2: PDF Extraction with PyMuPDF** - **REPLACEMENT REQUIRED**
   - Current: PyMuPDF-based text extraction with coordinates
   - New: PDFMathTranslate-based extraction with AI layout detection
   - Impact: Complete rewrite of extraction service

2. **Story 2.6: PDF Reconstruction & S3 Upload** - **REPLACEMENT REQUIRED**
   - Current: PyMuPDF-based reconstruction
   - New: PDFMathTranslate-based reconstruction
   - Impact: Complete rewrite of reconstruction service

3. **Story 2.3: DeepL Translation Integration** - **MODIFICATION REQUIRED**
   - Current: Separate translation step using DeepL API
   - New: May integrate with PDFMathTranslate's translation flow
   - Impact: Pipeline restructuring may be needed

**Unaffected Stories:**
- Story 2.1: File Upload Endpoint - No changes
- Story 2.4: Celery Job Queue Setup - No changes (orchestration remains)
- Story 2.5: Status Polling Endpoint - No changes

### Story Impact

**Current Stories Requiring Changes:**

**Story 2.2 Changes:**
- Replace `PDFService.extract_text_with_layout()` implementation
- Replace PyMuPDF with PDFMathTranslate API
- Update block extraction logic to use PDFMathTranslate's output format
- Maintain Redis caching strategy (adapt to new data format)
- Update coordinate system if PDFMathTranslate uses different format

**Story 2.6 Changes:**
- Replace `PDFReconstructionService.reconstruct_pdf()` implementation
- Use PDFMathTranslate's reconstruction capabilities
- Update S3 upload logic (may remain the same)
- Maintain tone customization support (adapt to new format)

**Story 2.3 Changes:**
- Evaluate if PDFMathTranslate handles translation internally
- If yes: Integrate PDFMathTranslate's translation service
- If no: Maintain DeepL integration but adapt to new block format
- Update translation flow to work with PDFMathTranslate's data structures

### Artifact Conflicts

**PRD (Product Requirements Document):**
- ✅ **No conflicts** - PRD requirements remain the same
- Format preservation requirement aligns with PDFMathTranslate's strength
- Translation quality requirements unchanged
- Processing time requirements may need adjustment (to be tested)

**Architecture Document:**
- ⚠️ **Section 4.1: PDF Processing & Layout Detection** - **UPDATE REQUIRED**
  - Current: PyMuPDF for extraction, PyMuPDF for reconstruction
  - New: PDFMathTranslate for end-to-end processing
  - Update technology stack table
  - Update processing pipeline diagram

- ⚠️ **Section 4.4: PDF Reconstruction & Editing Flow** - **UPDATE REQUIRED**
  - Current: PyMuPDF-based reconstruction
  - New: PDFMathTranslate-based reconstruction
  - Update reconstruction algorithm description

- ⚠️ **Processing Pipeline Section** - **UPDATE REQUIRED**
  - Current: Extract → Translate → Reconstruct (3 separate steps)
  - New: May be Extract+Translate+Reconstruct (integrated) or similar structure
  - Update pipeline flow diagram

**Epic 2 Tech Stack Document:**
- ⚠️ **PDF Processing Stack Section** - **MAJOR UPDATE REQUIRED**
  - Replace PyMuPDF entries with PDFMathTranslate
  - Update component table
  - Update story-to-tech mapping

**Sprint Artifacts:**
- ⚠️ **Story 2.2 Artifact** - **REPLACEMENT REQUIRED**
  - Create new story artifact for PDFMathTranslate extraction
  - Archive or update existing PyMuPDF story

- ⚠️ **Story 2.6 Artifact** - **REPLACEMENT REQUIRED**
  - Create new story artifact for PDFMathTranslate reconstruction
  - Archive or update existing PyMuPDF story

- ⚠️ **Story 2.3 Artifact** - **UPDATE MAY BE REQUIRED**
  - Update if translation integration changes

### Technical Impact

**Code Changes Required:**

1. **New Dependencies:**
   - Add `pdf2zh` package (PDFMathTranslate Python package)
   - May require additional dependencies (check PDFMathTranslate requirements)
   - Update `pyproject.toml` or `requirements.txt`

2. **Service Layer Changes:**
   - `backend/app/services/pdf_service.py` - Complete rewrite
   - `backend/app/services/pdf_reconstruction.py` - Complete rewrite
   - `backend/app/services/translation_service.py` - May need updates

3. **Task Layer Changes:**
   - `backend/app/tasks/extract_pdf.py` - Update to use PDFMathTranslate
   - `backend/app/tasks/reconstruct_pdf.py` - Update to use PDFMathTranslate
   - `backend/app/tasks/translate_blocks.py` - May need updates
   - `backend/app/tasks/orchestrator.py` - May need pipeline restructuring

4. **Schema Changes:**
   - `backend/app/schemas/pdf.py` - May need updates if data format changes
   - Block structure may need adaptation

5. **Test Changes:**
   - All PDF extraction tests need rewriting
   - All PDF reconstruction tests need rewriting
   - Integration tests need updates

**Infrastructure Impact:**
- No infrastructure changes required
- Same S3, Redis, PostgreSQL usage
- Celery orchestration remains the same

**Performance Impact:**
- To be determined through testing
- PDFMathTranslate may have different performance characteristics
- May require performance optimization

---

## 3. Recommended Approach

### Selected Path: Direct Adjustment (Option 1)

**Approach:** Replace PyMuPDF with PDFMathTranslate in Stories 2.2 and 2.6, modify Story 2.3 as needed.

### Rationale

1. **Maintains Project Timeline**
   - No epic resequencing required
   - Epic 2 remains in same position
   - No impact on Epic 3 or Epic 4

2. **Improves Quality**
   - Better format preservation for technical documents
   - AI-powered layout detection (DocLayout-YOLO)
   - Specialized for scientific/technical documents

3. **Library Ready**
   - PDFMathTranslate is available and documented
   - Open source with active development
   - Python API available (`pdf2zh` package)

4. **Scope Contained**
   - Affects Epic 2 stories only
   - Frontend remains unchanged
   - Infrastructure remains unchanged

5. **Risk Manageable**
   - Open source library
   - Well-documented
   - Can test integration before full replacement

### Effort Estimate

- **Story 2.2 Replacement:** 1.5-2 days
  - Research PDFMathTranslate API
  - Rewrite extraction service
  - Update tests
  - Integration testing

- **Story 2.6 Replacement:** 1.5-2 days
  - Rewrite reconstruction service
  - Update tests
  - Integration testing

- **Story 2.3 Modification:** 0.5-1 day
  - Evaluate translation integration
  - Update if needed
  - Testing

- **Documentation Updates:** 0.5 day
  - Update architecture document
  - Update Epic 2 tech stack
  - Update sprint artifacts

**Total Effort:** 4-5.5 days

### Risk Assessment

**Technical Risk:** Medium
- New library integration
- May have different API patterns
- Performance characteristics unknown
- Mitigation: Thorough testing, fallback plan

**Timeline Risk:** Low
- Effort estimate is reasonable
- No epic resequencing
- Can be done within Epic 2 timeline

**Quality Risk:** Low
- PDFMathTranslate is proven for technical documents
- Should improve output quality
- Mitigation: Extensive testing with technical PDFs

**Team Morale Risk:** Low
- Clear improvement path
- No major architectural changes
- Maintains existing structure

### Timeline Impact

- **Epic 2 Duration:** May extend by 1-2 days if needed
- **Epic 3 Start:** No impact (frontend unchanged)
- **Epic 4 Start:** No impact
- **MVP Launch:** No impact on target date

---

## 4. Detailed Change Proposals

### Change Proposal 1: Story 2.2 - PDF Extraction

**Story:** 2-2-pdf-extraction  
**Type:** Replacement

**OLD Implementation:**
```python
# backend/app/services/pdf_service.py
class PDFService:
    @staticmethod
    def extract_text_with_layout(pdf_path: str) -> PDFExtractionResult:
        # PyMuPDF-based extraction
        doc = fitz.open(pdf_path)
        # ... PyMuPDF extraction logic
```

**NEW Implementation:**
```python
# backend/app/services/pdf_service.py
class PDFService:
    @staticmethod
    def extract_text_with_layout(pdf_path: str) -> PDFExtractionResult:
        # PDFMathTranslate-based extraction
        from pdf2zh import translate
        # Use PDFMathTranslate API for extraction
        # Adapt output to existing PDFExtractionResult schema
```

**Rationale:**
- PDFMathTranslate provides better layout detection for technical documents
- AI-powered detection (DocLayout-YOLO) handles complex layouts better
- Maintains existing interface for compatibility

**Files to Modify:**
- `backend/app/services/pdf_service.py` - Complete rewrite
- `backend/app/tasks/extract_pdf.py` - Update to use new service
- `backend/app/schemas/pdf.py` - May need schema updates
- `backend/tests/test_pdf_extraction.py` - Rewrite tests

---

### Change Proposal 2: Story 2.6 - PDF Reconstruction

**Story:** 2-6-pdf-reconstruction  
**Type:** Replacement

**OLD Implementation:**
```python
# backend/app/services/pdf_reconstruction.py
class PDFReconstructionService:
    @staticmethod
    def reconstruct_pdf(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        # PyMuPDF-based reconstruction
        pdf_doc = fitz.open(stream=original_pdf_bytes)
        # ... PyMuPDF reconstruction logic
```

**NEW Implementation:**
```python
# backend/app/services/pdf_reconstruction.py
class PDFReconstructionService:
    @staticmethod
    def reconstruct_pdf(
        original_pdf_bytes: bytes,
        translated_blocks: List[TranslatedBlock],
    ) -> bytes:
        # PDFMathTranslate-based reconstruction
        from pdf2zh import translate
        # Use PDFMathTranslate API for reconstruction
        # May integrate translation if PDFMathTranslate handles it
```

**Rationale:**
- PDFMathTranslate provides better format preservation
- Handles complex layouts (tables, equations) better
- May provide integrated translation+reconstruction

**Files to Modify:**
- `backend/app/services/pdf_reconstruction.py` - Complete rewrite
- `backend/app/tasks/reconstruct_pdf.py` - Update to use new service
- `backend/tests/test_pdf_reconstruction.py` - Rewrite tests

---

### Change Proposal 3: Story 2.3 - Translation Integration

**Story:** 2-3-deepl-translation  
**Type:** Modification (if needed)

**Evaluation Required:**
- Check if PDFMathTranslate handles translation internally
- If yes: Integrate PDFMathTranslate's translation service
- If no: Maintain DeepL integration but adapt to new block format

**Rationale:**
- PDFMathTranslate may provide integrated translation
- If integrated, simplifies pipeline (fewer steps)
- If separate, maintain DeepL for quality control

**Files to Modify (if needed):**
- `backend/app/services/translation_service.py` - May need updates
- `backend/app/tasks/translate_blocks.py` - May need updates
- `backend/app/tasks/orchestrator.py` - May need pipeline restructuring

---

### Change Proposal 4: Epic 2 Tech Stack Document

**File:** `docs/epic-2-tech-stack.md`  
**Type:** Update

**OLD Content:**
```markdown
### **PDF Processing Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **PDF Library** | PyMuPDF (fitz) | 1.23+ | Fast text extraction with coordinates | Story 2.2 |
| **Text Extraction** | PyMuPDF blocks | - | Per-page block extraction | Story 2.2 |
```

**NEW Content:**
```markdown
### **PDF Processing Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **PDF Library** | PDFMathTranslate (pdf2zh) | Latest | AI-powered layout detection, specialized for technical docs | Story 2.2 |
| **Layout Detection** | DocLayout-YOLO | - | AI model for precise layout detection | Story 2.2 |
| **Text Extraction** | PDFMathTranslate API | - | Per-page block extraction with layout preservation | Story 2.2 |
```

**Rationale:**
- Document technology change
- Update component table
- Update story-to-tech mapping

---

### Change Proposal 5: Architecture Document

**File:** `docs/architecture.md`  
**Type:** Update

**Sections to Update:**

1. **Section 4.1: PDF Processing & Layout Detection**
   - Replace PyMuPDF references with PDFMathTranslate
   - Update processing algorithm description
   - Update performance characteristics

2. **Section 4.4: PDF Reconstruction & Editing Flow**
   - Update reconstruction algorithm
   - Update to reflect PDFMathTranslate approach

3. **Processing Pipeline Section**
   - Update pipeline flow diagram
   - Update step descriptions

**Rationale:**
- Keep architecture document accurate
- Reflect new technology choices
- Maintain documentation consistency

---

## 5. Implementation Handoff

### Change Scope Classification

**Classification:** **MODERATE**

- **Scope:** Backend service layer changes
- **Impact:** 3 stories in Epic 2
- **Complexity:** Medium (library integration, testing required)
- **Risk:** Medium (new library, performance unknown)

### Handoff Recipients

**Primary:** Backend Development Team
- **Responsibilities:**
  - Research PDFMathTranslate API and integration patterns
  - Implement Story 2.2 replacement (extraction)
  - Implement Story 2.6 replacement (reconstruction)
  - Evaluate and modify Story 2.3 (translation) if needed
  - Update all tests
  - Performance testing and optimization

**Secondary:** Product Owner / Scrum Master
- **Responsibilities:**
  - Review and approve change proposal
  - Update sprint backlog if needed
  - Coordinate with team on timeline
  - Update Epic 2 status

**Tertiary:** Technical Writer (if available)
- **Responsibilities:**
  - Update architecture document
  - Update Epic 2 tech stack document
  - Update sprint artifacts

### Implementation Tasks

**Phase 1: Research & Planning (0.5 day)**
- [ ] Research PDFMathTranslate Python API
- [ ] Review PDFMathTranslate documentation
- [ ] Understand data format and integration patterns
- [ ] Create integration plan
- [ ] Identify compatibility points with existing code

**Phase 2: Story 2.2 Replacement (1.5-2 days)**
- [ ] Install `pdf2zh` package
- [ ] Rewrite `PDFService.extract_text_with_layout()`
- [ ] Adapt PDFMathTranslate output to existing schema
- [ ] Update `extract_pdf.py` task
- [ ] Rewrite extraction tests
- [ ] Integration testing

**Phase 3: Story 2.6 Replacement (1.5-2 days)**
- [ ] Rewrite `PDFReconstructionService.reconstruct_pdf()`
- [ ] Integrate PDFMathTranslate reconstruction
- [ ] Update `reconstruct_pdf.py` task
- [ ] Maintain tone customization support
- [ ] Rewrite reconstruction tests
- [ ] Integration testing

**Phase 4: Story 2.3 Evaluation (0.5-1 day)**
- [ ] Evaluate PDFMathTranslate translation capabilities
- [ ] Decide: integrate or maintain DeepL
- [ ] Update translation service if needed
- [ ] Update orchestrator if pipeline changes
- [ ] Testing

**Phase 5: Documentation (0.5 day)**
- [ ] Update architecture document
- [ ] Update Epic 2 tech stack document
- [ ] Update sprint artifacts
- [ ] Create migration notes

**Phase 6: Testing & Validation (1 day)**
- [ ] End-to-end pipeline testing
- [ ] Performance testing with technical PDFs
- [ ] Format preservation validation
- [ ] Regression testing
- [ ] Load testing

### Success Criteria

**Technical Success:**
- ✅ PDFMathTranslate integrated successfully
- ✅ Extraction working with technical PDFs
- ✅ Reconstruction preserving complex layouts
- ✅ All tests passing
- ✅ Performance acceptable (<90 seconds for 100-page PDF)

**Quality Success:**
- ✅ Format preservation improved for technical documents
- ✅ Tables, equations, multi-column layouts preserved
- ✅ No regression in simple document handling

**Process Success:**
- ✅ Documentation updated
- ✅ Team trained on new library
- ✅ Epic 2 completed on schedule

### Risk Mitigation

**Risk 1: PDFMathTranslate API Complexity**
- **Mitigation:** Thorough research phase, proof-of-concept before full implementation
- **Fallback:** Maintain PyMuPDF as backup option

**Risk 2: Performance Degradation**
- **Mitigation:** Performance testing early, optimization if needed
- **Fallback:** Optimize or consider hybrid approach

**Risk 3: Data Format Incompatibility**
- **Mitigation:** Adapter layer to maintain existing schema
- **Fallback:** Update schema if necessary

**Risk 4: Integration Issues**
- **Mitigation:** Incremental integration, extensive testing
- **Fallback:** Rollback plan ready

---

## 6. Next Steps

### Immediate Actions

1. **Review & Approval**
   - [ ] Product Owner reviews this proposal
   - [ ] Technical lead reviews technical feasibility
   - [ ] Team reviews effort estimates
   - [ ] Get approval to proceed

2. **Research Phase**
   - [ ] Research PDFMathTranslate Python API
   - [ ] Create proof-of-concept
   - [ ] Validate integration approach
   - [ ] Refine effort estimates

3. **Implementation Planning**
   - [ ] Break down into tasks
   - [ ] Assign to developers
   - [ ] Update sprint backlog
   - [ ] Set timeline

### Timeline

- **Week 1:** Research & Planning + Story 2.2 replacement
- **Week 2:** Story 2.6 replacement + Story 2.3 evaluation
- **Week 3:** Documentation + Testing + Validation

**Target Completion:** Within Epic 2 timeline (Dec 9-13, with possible 1-2 day extension)

---

## 7. Approval

**Proposal Status:** ✅ **APPROVED**

**Reviewers:**
- [x] Product Owner: Roy
- [x] Technical Lead: Approved
- [x] Backend Team Lead: Approved
- [x] Scrum Master: Approved

**Approval Required From:**
- [x] Product Owner: Roy
- [x] Technical Lead: Approved

**Date Approved:** December 13, 2025

---

## Appendix: References

- **PDFMathTranslate GitHub:** https://github.com/PDFMathTranslate/PDFMathTranslate
- **Research Document:** `docs/research.md` (Section 4.1, Option B)
- **Current Implementation:** 
  - `backend/app/services/pdf_service.py`
  - `backend/app/services/pdf_reconstruction.py`
- **Epic 2 Tech Stack:** `docs/epic-2-tech-stack.md`
- **Architecture Document:** `docs/architecture.md`

---

**Document Version:** 1.0 (APPROVED)  
**Last Updated:** December 13, 2025  
**Status:** ✅ Approved - Ready for Implementation
