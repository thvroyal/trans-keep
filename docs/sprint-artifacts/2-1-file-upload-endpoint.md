# Story 2.1: File Upload Endpoint

**Story Key:** 2-1-file-upload-endpoint  
**Epic:** 2 - Core Translation Pipeline  
**Week:** Week 2 (Dec 9-13)  
**Duration:** 1.5 days  
**Owner:** Backend Developer  
**Status:** backlog  

---

## Overview

Implement POST /api/v1/upload endpoint that accepts PDF files up to 100MB, validates file type and size, stores to S3, creates translation record in database, and returns job_id for status polling.

---

## Acceptance Criteria

### AC 2.1.1: Upload Endpoint Implemented ✅
- [ ] POST /api/v1/upload endpoint working
- [ ] Accepts multipart/form-data with file
- [ ] Returns job_id and upload_token
- [ ] Requires authentication (JWT)

### AC 2.1.2: File Validation ✅
- [ ] Validates file type (PDF only)
- [ ] Validates file size (≤100MB)
- [ ] Rejects invalid files with clear error
- [ ] Prevents file upload attacks

### AC 2.1.3: S3 Storage ✅
- [ ] Files uploaded to S3 (or MinIO locally)
- [ ] Temporary upload location used
- [ ] File deleted after 24 hours (cleanup job)
- [ ] boto3 properly configured

### AC 2.1.4: Database Record Created ✅
- [ ] Translation record created in DB
- [ ] Status set to "pending"
- [ ] User ID associated
- [ ] Timestamps recorded

### AC 2.1.5: Frontend Integration ✅
- [ ] File drop zone on UploadPage
- [ ] Progress indicator during upload
- [ ] Error handling and display
- [ ] Redirect to ProcessingPage after upload

---

## Tasks & Subtasks

### Task 1: Create Upload Endpoint
- [ ] Define request schema (multipart/form-data)
- [ ] Create POST /api/v1/upload route
- [ ] Implement file stream handling
- [ ] Implement response with job_id
- [ ] Add request logging

**Estimated Time:** 2 hours

### Task 2: Implement File Validation
- [ ] Check Content-Type header (application/pdf)
- [ ] Validate file size before upload
- [ ] Add custom error messages
- [ ] Test with invalid files
- [ ] Add rate limiting (10 files/user/day)

**Estimated Time:** 1.5 hours

### Task 3: Implement S3 Upload
- [ ] Create S3 key naming convention
- [ ] Upload file in chunks for large files
- [ ] Generate pre-signed URL for download
- [ ] Implement error retry logic
- [ ] Test with 10MB, 100MB files

**Estimated Time:** 2 hours

### Task 4: Create Database Record
- [ ] Create Translation model
- [ ] Insert record on successful upload
- [ ] Set status = "pending"
- [ ] Handle database errors gracefully
- [ ] Return job_id in response

**Estimated Time:** 1.5 hours

### Task 5: Build Frontend UI
- [ ] Create file drop zone component
- [ ] Add drag & drop support
- [ ] Show upload progress
- [ ] Handle errors and display them
- [ ] Redirect to /processing/{job_id}

**Estimated Time:** 2.5 hours

### Task 6: Integration Testing
- [ ] Test full upload flow with small PDF
- [ ] Test with 100MB PDF
- [ ] Test with invalid files
- [ ] Test error handling
- [ ] Test database record creation

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Use chunked upload for files >10MB
- Store original filename (sanitized) in DB
- Generate unique job_id (UUID) for tracking
- Implement server-side file type validation
- Set S3 cleanup lifecycle policy (24 hour expiration)

**S3 Key Format:**
```
uploads/{user_id}/{job_id}/{original_filename}.pdf
```

**Response Schema:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "File uploaded successfully"
}
```

**Resources:**
- boto3 documentation
- FastAPI file upload docs
- React drop zone libraries

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Tests passing (100% coverage of upload flow)
- ✅ Frontend UI responsive
- ✅ Error messages clear
- ✅ Ready for Story 2.2

---

## File List

**New Files:**
- [ ] backend/app/routers/upload.py
- [ ] backend/app/schemas/upload.py
- [ ] backend/app/services/s3_service.py
- [ ] frontend/src/pages/UploadPage.tsx
- [ ] frontend/src/components/FileDropZone.tsx
- [ ] backend/tests/test_upload.py

---

## Dev Agent Record

### Debug Log
*To be filled in during development*

### Completion Notes
*To be filled in after story completion*

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  

---

## Context Reference

- **Story Context File:** docs/sprint-artifacts/2-1-file-upload-endpoint.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

