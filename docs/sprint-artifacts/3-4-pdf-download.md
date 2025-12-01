# Story 3.4: PDF Download Endpoint

**Story Key:** 3-4-pdf-download  
**Epic:** 3 - UI Polish & Refinement  
**Week:** Week 3 (Dec 16-20)  
**Duration:** 1 day  
**Owner:** Backend Developer  
**Status:** backlog  

---

## Overview

Implement GET /api/v1/download/{job_id} endpoint that applies user edits, reconstructs PDF with translated text, and provides download link.

---

## Acceptance Criteria

### AC 3.4.1: Download Endpoint ✅
- [ ] GET /api/v1/download/{job_id} returns presigned URL
- [ ] PDF properly reconstructed with translations
- [ ] User edits applied to final PDF
- [ ] Requires authentication

### AC 3.4.2: PDF Reconstruction ✅
- [ ] Uses original PDF + translated blocks
- [ ] Applies user edits from frontend
- [ ] Preserves original layout and formatting
- [ ] Handles multi-page PDFs

### AC 3.4.3: S3 Integration ✅
- [ ] Final PDF stored in S3
- [ ] Pre-signed URL valid for 1 hour
- [ ] CloudFront distribution for CDN
- [ ] Browser downloads directly

### AC 3.4.4: File Management ✅
- [ ] Original PDF cleaned up after 24 hours
- [ ] Final PDF cleaned up after 24 hours
- [ ] User can download multiple times
- [ ] Storage optimized

### AC 3.4.5: Frontend Integration ✅
- [ ] Download button on review page
- [ ] Shows download progress
- [ ] Error handling
- [ ] Success notification

---

## Tasks & Subtasks

### Task 1: Create PDF Reconstruction Logic
- [ ] Load original PDF blocks
- [ ] Apply translated text to coordinates
- [ ] Apply user edits (overwrite translated)
- [ ] Handle font and layout
- [ ] Test with various PDFs

**Estimated Time:** 2 hours

### Task 2: Implement Download Endpoint
- [ ] Create GET /api/v1/download/{job_id}
- [ ] Verify user owns translation
- [ ] Call reconstruction service
- [ ] Upload to S3
- [ ] Return pre-signed URL

**Estimated Time:** 1.5 hours

### Task 3: Add Frontend UI
- [ ] Create download button
- [ ] Show download progress
- [ ] Handle download completion
- [ ] Handle errors
- [ ] Track download analytics

**Estimated Time:** 1.5 hours

### Task 4: S3 & CloudFront Setup
- [ ] Configure S3 bucket for downloads
- [ ] Set up CloudFront distribution
- [ ] Configure cache headers
- [ ] Test download speed
- [ ] Verify CDN working

**Estimated Time:** 1.5 hours

### Task 5: File Cleanup Jobs
- [ ] Create Celery beat task
- [ ] Delete files older than 24 hours
- [ ] Run every hour
- [ ] Track cleanup stats
- [ ] Alert on failures

**Estimated Time:** 1 hour

### Task 6: Testing & Performance
- [ ] Test download with small PDF
- [ ] Test download with 500-page PDF
- [ ] Verify edits preserved
- [ ] Test CloudFront CDN
- [ ] Load test concurrent downloads

**Estimated Time:** 1.5 hours

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
