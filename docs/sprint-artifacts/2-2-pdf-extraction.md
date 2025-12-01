# Story 2.2: PDF Extraction with PyMuPDF

**Story Key:** 2-2-pdf-extraction  
**Epic:** 2 - Core Translation Pipeline  
**Week:** Week 2 (Dec 9-13)  
**Duration:** 1.5 days  
**Owner:** Backend Developer  
**Status:** backlog  

---

## Overview

Extract text from PDF files with layout preservation using PyMuPDF (fitz). Capture text blocks with exact coordinates for later reconstruction. Handle 10, 100, 500+ page PDFs efficiently.

---

## Acceptance Criteria

### AC 2.2.1: PDF Text Extraction ✅
- [ ] extract_text_with_layout() function working
- [ ] Returns text blocks with coordinates
- [ ] Captures page and block numbers
- [ ] Handles multi-line text blocks

### AC 2.2.2: Layout Preservation ✅
- [ ] Text block positions captured
- [ ] Font information stored
- [ ] Text rotation handled
- [ ] Column detection working

### AC 2.2.3: Performance ✅
- [ ] 10-page PDF: <1 second
- [ ] 100-page PDF: <5 seconds
- [ ] 500-page PDF: <20 seconds
- [ ] Redis caching for extracted data

### AC 2.2.4: Error Handling ✅
- [ ] Scanned PDFs detected and flagged
- [ ] Corrupted PDFs handled gracefully
- [ ] Large PDFs don't crash system
- [ ] Clear error messages

### AC 2.2.5: Integration ✅
- [ ] Integrated with upload flow
- [ ] Extraction triggered after upload
- [ ] Results cached in Redis
- [ ] Ready for translation pipeline

---

## Tasks & Subtasks

### Task 1: Create PDF Extraction Module
- [ ] Install PyMuPDF and dependencies
- [ ] Create extract_text_with_layout() function
- [ ] Return structured data (blocks with coordinates)
- [ ] Handle text rotation and scaling
- [ ] Test with various PDF formats

**Estimated Time:** 2 hours

### Task 2: Implement Block Extraction
- [ ] Extract individual text blocks
- [ ] Capture block coordinates (x, y, width, height)
- [ ] Preserve formatting (bold, italic, font size)
- [ ] Handle multi-line blocks
- [ ] Create Block data structure

**Estimated Time:** 2 hours

### Task 3: Performance Optimization
- [ ] Implement multi-threading for page processing
- [ ] Cache results in Redis for 24 hours
- [ ] Implement progress tracking
- [ ] Benchmark extraction times
- [ ] Optimize for large PDFs

**Estimated Time:** 2 hours

### Task 4: Handle Edge Cases
- [ ] Detect scanned PDFs (no embedded text)
- [ ] Handle corrupted PDF sections
- [ ] Skip empty pages
- [ ] Handle different text encodings
- [ ] Log warnings for issues

**Estimated Time:** 1.5 hours

### Task 5: Integrate with Upload Flow
- [ ] Create extraction Celery task
- [ ] Trigger after file stored in S3
- [ ] Update translation status
- [ ] Store blocks in database
- [ ] Handle extraction failures

**Estimated Time:** 2 hours

### Task 6: Performance Testing
- [ ] Test with 10-page PDF
- [ ] Test with 100-page PDF
- [ ] Test with 500-page PDF
- [ ] Measure timing at each step
- [ ] Verify memory usage

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- PyMuPDF provides exact text positions and coordinates
- Use page-based processing for memory efficiency
- Cache extracted blocks to avoid re-extraction
- Scanned PDFs will be marked for future Phase 2 (OCR)
- Store coordinates as normalized percentages (0-100)

**Block Structure:**
```python
{
  "page": 1,
  "block_id": 0,
  "text": "Sample text",
  "coordinates": {
    "x": 10.5,
    "y": 20.3,
    "width": 80.0,
    "height": 5.0
  },
  "font_size": 12,
  "is_scanned": false
}
```

**Resources:**
- PyMuPDF documentation
- Performance optimization techniques
- Redis caching patterns

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Performance benchmarks met
- ✅ Error handling verified
- ✅ Caching working
- ✅ Ready for Story 2.3

---

## File List

**New Files:**
- [ ] backend/app/services/pdf_service.py
- [ ] backend/app/schemas/pdf.py
- [ ] backend/app/tasks/extract_pdf.py
- [ ] backend/tests/test_pdf_extraction.py
- [ ] backend/tests/fixtures/sample_pdfs/ (test PDFs)

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  

---

## Context Reference

- **Story Context File:** docs/sprint-artifacts/2-2-pdf-extraction.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

