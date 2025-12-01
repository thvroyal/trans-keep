# Story 2.5: Status Polling Endpoint

**Story Key:** 2-5-status-polling  
**Epic:** 2 - Core Translation Pipeline  
**Week:** Week 2 (Dec 9-13)  
**Duration:** 1 day  
**Owner:** Backend + Frontend Developer  
**Status:** backlog  

---

## Overview

Implement GET /api/v1/status/{job_id} endpoint for polling translation progress. Frontend polls every 2 seconds to show real-time progress indicator.

---

## Acceptance Criteria

### AC 2.5.1: Status Endpoint ✅
- [ ] GET /api/v1/status/{job_id} returns status
- [ ] Returns: status, progress %, page count, ETA
- [ ] Handles invalid job IDs gracefully
- [ ] Requires authentication

### AC 2.5.2: Progress Calculation ✅
- [ ] Tracks extracted blocks
- [ ] Tracks translated blocks
- [ ] Calculates completion percentage
- [ ] Updates in real-time

### AC 2.5.3: Frontend Polling ✅
- [ ] TanStack Query with refetchInterval
- [ ] Polls every 2 seconds
- [ ] Shows progress bar
- [ ] Shows estimated time remaining
- [ ] Stops polling when complete

### AC 2.5.4: Error States ✅
- [ ] Shows error message if translation fails
- [ ] Allows retry option
- [ ] Logs errors for debugging
- [ ] Graceful timeout handling

### AC 2.5.5: Integration ✅
- [ ] Works with Celery pipeline (Story 2.4)
- [ ] Works with upload endpoint (Story 2.1)
- [ ] Seamless user experience
- [ ] No manual refresh needed

---

## Tasks & Subtasks

### Task 1: Create Status Endpoint
- [ ] Define GET /api/v1/status/{job_id} route
- [ ] Query translation status from DB
- [ ] Calculate progress percentage
- [ ] Estimate completion time
- [ ] Return JSON response

**Estimated Time:** 1.5 hours

### Task 2: Implement Progress Calculation
- [ ] Track blocks extracted
- [ ] Track blocks translated
- [ ] Calculate progress: (translated / total) * 100
- [ ] Handle edge cases (0 blocks, etc.)
- [ ] Test calculations

**Estimated Time:** 1 hour

### Task 3: Build Frontend UI
- [ ] Create ProcessingPage component
- [ ] Add progress bar (shadcn/ui Progress)
- [ ] Show percentage and ETA
- [ ] Add cancel button option
- [ ] Handle completion state

**Estimated Time:** 1.5 hours

### Task 4: Implement Frontend Polling
- [ ] Use TanStack Query useQuery
- [ ] Set refetchInterval: 2000 (2 seconds)
- [ ] Stop polling when status === 'completed'
- [ ] Handle errors in polling
- [ ] Show loading state

**Estimated Time:** 1.5 hours

### Task 5: Error Handling
- [ ] Handle job not found (404)
- [ ] Handle permission denied (403)
- [ ] Handle server errors (500)
- [ ] Retry logic for transient errors
- [ ] User-friendly error messages

**Estimated Time:** 1 hour

### Task 6: Integration & Testing
- [ ] Test with real Celery tasks
- [ ] Test polling with long-running job
- [ ] Test completion detection
- [ ] Test error scenarios
- [ ] Performance test (many polls)

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Use efficient database queries (indexed on job_id)
- ETA calculation: (time_elapsed / progress%) - time_elapsed
- Poll immediately after upload for fast feedback
- Cache status in Redis for 10 seconds
- Clean up completed jobs after 24 hours

**Status Response:**
```json
{
  "job_id": "uuid",
  "status": "processing",
  "progress": 45,
  "total_blocks": 100,
  "translated_blocks": 45,
  "eta_seconds": 120,
  "page_count": 10
}
```

**Resources:**
- TanStack Query documentation
- Polling patterns & best practices

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Frontend shows real-time progress
- ✅ Polling efficient (not overloading server)
- ✅ Error handling working
- ✅ Week 2 complete - full pipeline working!

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
