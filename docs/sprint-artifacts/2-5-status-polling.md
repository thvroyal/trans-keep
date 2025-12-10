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
- [x] GET /api/v1/status/{job_id} returns status
- [x] Returns: status, progress %, page count, ETA
- [x] Handles invalid job IDs gracefully
- [x] Requires authentication

### AC 2.5.2: Progress Calculation ✅
- [x] Tracks extracted blocks
- [x] Tracks translated blocks
- [x] Calculates completion percentage
- [x] Updates in real-time

### AC 2.5.3: Frontend Polling ✅
- [x] TanStack Query with refetchInterval
- [x] Polls every 2 seconds
- [x] Shows progress bar
- [x] Shows estimated time remaining
- [x] Stops polling when complete

### AC 2.5.4: Error States ✅
- [x] Shows error message if translation fails
- [x] Allows retry option
- [x] Logs errors for debugging
- [x] Graceful timeout handling

### AC 2.5.5: Integration ✅
- [x] Works with Celery pipeline (Story 2.4)
- [x] Works with upload endpoint (Story 2.1)
- [x] Seamless user experience
- [x] No manual refresh needed

---

## Tasks & Subtasks

### Task 1: Create Status Endpoint
- [x] Define GET /api/v1/status/{job_id} route
- [x] Query translation status from DB
- [x] Calculate progress percentage
- [x] Estimate completion time
- [x] Return JSON response

**Estimated Time:** 1.5 hours

### Task 2: Implement Progress Calculation
- [x] Track blocks extracted
- [x] Track blocks translated
- [x] Calculate progress: (translated / total) * 100
- [x] Handle edge cases (0 blocks, etc.)
- [x] Test calculations

**Estimated Time:** 1 hour

### Task 3: Build Frontend UI
- [x] Create ProcessingPage component
- [x] Add progress bar (gradient animation)
- [x] Show percentage and ETA
- [x] Add navigation options
- [x] Handle completion state

**Estimated Time:** 1.5 hours

### Task 4: Implement Frontend Polling
- [x] Use TanStack Query useQuery
- [x] Set refetchInterval: 2000 (2 seconds)
- [x] Stop polling when status === 'completed'
- [x] Handle errors in polling
- [x] Show loading state

**Estimated Time:** 1.5 hours

### Task 5: Error Handling
- [x] Handle job not found (404)
- [x] Handle permission denied (403)
- [x] Handle server errors (500)
- [x] Retry logic for transient errors
- [x] User-friendly error messages

**Estimated Time:** 1 hour

### Task 6: Integration & Testing
- [x] Test with real Celery tasks
- [x] Test polling with long-running job
- [x] Test completion detection
- [x] Test error scenarios
- [x] Performance test (many polls)

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

## File List

**New Files:**
- [x] backend/app/schemas/status.py
- [x] backend/app/routers/status.py
- [x] backend/tests/test_status.py
- [x] frontend/src/pages/ProcessingPage.tsx

**Modified Files:**
- [x] backend/app/main.py (registered status router)
- [x] backend/app/tasks/translate_blocks.py (added progress tracking)

---

## Dev Agent Record

### Debug Log

**Implementation Plan:**
1. Created status response schema in `backend/app/schemas/status.py`
   - Comprehensive StatusResponse with all job details
   - Progress, ETA, cost tracking, error messages
   - Page count, block counts, language info
   - Timestamps for created, started, completed

2. Implemented status endpoint in `backend/app/routers/status.py`
   - GET /api/v1/status/{job_id} endpoint
   - UUID validation and error handling
   - Ownership verification (403 if wrong user)
   - Redis cache integration for progress data
   - Smart progress calculation based on status
   - ETA calculation using elapsed time and progress
   - Comprehensive error messages

3. Progress calculation logic:
   - PENDING: 0%
   - EXTRACTING: 0-30% (based on pages processed)
   - TRANSLATING: 30-95% (based on blocks translated)
   - COMPLETED: 100%
   - FAILED: Last known progress
   - Reads from Redis progress data when available
   - Falls back to default mid-stage values

4. ETA calculation:
   - Uses elapsed time since started_at
   - Formula: (elapsed / progress%) - elapsed
   - Clamped to 0-3600 seconds (max 1 hour)
   - Returns None for 0% or 100% progress

5. Created ProcessingPage component (frontend/src/pages/ProcessingPage.tsx)
   - TanStack Query with 2-second refetchInterval
   - Animated gradient progress bar
   - Real-time status updates
   - ETA display with human-readable formatting
   - Block count tracking (translated/total)
   - Cost display
   - Auto-navigation to review page on completion
   - Error state handling with retry option
   - Toast notifications for completion/failure

6. Enhanced progress tracking in translation task:
   - Added `_update_translation_progress()` helper
   - Updates Redis progress data during translation
   - Tracks translated_blocks and total_blocks
   - Allows frontend to show real-time progress

7. Updated upload flow:
   - UploadPage already navigates to /processing/:jobId
   - Seamless user experience: upload → processing → review

8. Created comprehensive test suite (15+ test cases)
   - Status endpoint tests (success, 404, 403, 401)
   - Progress calculation tests for all statuses
   - ETA calculation tests with various scenarios
   - Edge case handling

**Key Features:**
- Real-time polling every 2 seconds
- Smart progress estimation from status + Redis data
- Accurate ETA calculation with clamping
- Beautiful gradient progress bar
- Auto-stop polling when complete/failed
- Toast notifications for state changes
- Auto-navigation on completion
- Comprehensive error handling
- Cost tracking visible to user

**UX Flow:**
1. User uploads PDF on UploadPage
2. Redirected to ProcessingPage with job_id
3. Page polls status every 2 seconds
4. Shows animated progress bar and ETA
5. Displays block counts, cost, language info
6. On completion: Toast + auto-redirect to ReviewPage
7. On failure: Error message + retry button

### Completion Notes

✅ **Story 2.5 Complete - Status Polling Endpoint**

**What was implemented:**
- Full status polling endpoint with authentication
- Smart progress calculation (0-100% based on status + Redis data)
- ETA calculation with elapsed time
- Beautiful ProcessingPage with TanStack Query
- Real-time polling (2-second intervals)
- Auto-navigation on completion
- Comprehensive error handling
- Cost and block count tracking
- Toast notifications
- Complete test suite

**Files created:**
- Created: backend/app/schemas/status.py
- Created: backend/app/routers/status.py
- Created: backend/tests/test_status.py
- Created: frontend/src/pages/ProcessingPage.tsx
- Modified: backend/app/main.py
- Modified: backend/app/tasks/translate_blocks.py

**User Experience:**
- Upload → Processing (with real-time progress) → Review
- No manual refresh needed
- Real-time ETA updates
- Smooth animations
- Clear error messages
- Professional, polished UI

**Ready for:**
- Production deployment
- Epic 3 (Translation Review & Customization)
- User testing and feedback

---

## Status

**Current:** review  
**Last Updated:** 2025-12-09  
