# Story 2.4: Celery Job Queue Setup

**Story Key:** 2-4-celery-job-queue  
**Epic:** 2 - Core Translation Pipeline  
**Week:** Week 2 (Dec 9-13)  
**Duration:** 1.5 days  
**Owner:** Backend Developer  
**Status:** backlog  

---

## Overview

Set up Celery task queue with Redis broker for asynchronous PDF processing. Orchestrate extraction, translation, tone customization, and PDF reconstruction as a task pipeline.

---

## Acceptance Criteria

### AC 2.4.1: Celery Configuration ✅
- [ ] Celery initialized with Redis broker
- [ ] Worker process running in docker-compose
- [ ] Task registry populated
- [ ] Celery Beat scheduler working

### AC 2.4.2: Task Orchestration ✅
- [ ] extract_and_translate task defined
- [ ] Task chain: extract → translate → tone → reconstruct
- [ ] Error handling in task chains
- [ ] Retry logic on failure

### AC 2.4.3: Monitoring ✅
- [ ] Task status tracked in database
- [ ] Job progress visible in API
- [ ] Failed tasks logged
- [ ] Celery logs in Jaeger

### AC 2.4.4: Integration ✅
- [ ] Triggered on file upload
- [ ] Status updates flow to frontend
- [ ] Long-running tasks don't block API
- [ ] Graceful timeout handling

### AC 2.4.5: Production Ready ✅
- [ ] Celery Flower (monitoring UI) available
- [ ] Worker health checks
- [ ] Automatic retry on worker failure
- [ ] Task timeouts configured

---

## Tasks & Subtasks

### Task 1: Set Up Celery
- [ ] Install celery and redis packages
- [ ] Create celery_app.py configuration
- [ ] Configure Redis broker
- [ ] Initialize worker in docker-compose
- [ ] Verify worker connects successfully

**Estimated Time:** 1.5 hours

### Task 2: Create Task Pipeline
- [ ] Define extract task
- [ ] Define translate task
- [ ] Define tone_customize task
- [ ] Define reconstruct task
- [ ] Create orchestration chain

**Estimated Time:** 2 hours

### Task 3: Implement Error Handling
- [ ] Add retry logic to tasks
- [ ] Handle task timeouts
- [ ] Log failures with context
- [ ] Implement dead letter queue
- [ ] Test failure scenarios

**Estimated Time:** 1.5 hours

### Task 4: Add Status Tracking
- [ ] Store task status in database
- [ ] Update status at each step
- [ ] Expose status via API
- [ ] Track progress percentage
- [ ] Calculate ETA

**Estimated Time:** 1.5 hours

### Task 5: Set Up Monitoring
- [ ] Install Celery Flower
- [ ] Expose Flower at localhost:5555
- [ ] Add task logging
- [ ] Integrate with Otel tracing
- [ ] Monitor resource usage

**Estimated Time:** 1 hour

### Task 6: Integration Testing
- [ ] Test full pipeline with real PDF
- [ ] Test failure recovery
- [ ] Test timeout handling
- [ ] Verify status updates
- [ ] Load test with multiple jobs

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Use task chains (Celery signatures) for orchestration
- Set reasonable timeouts (5 min for extraction, 10 min for translation)
- Implement idempotent tasks (can safely retry)
- Store intermediate results in Redis
- Monitor worker health constantly

**Task Pipeline Flow:**
```
Upload → extract_and_translate_task() 
       → extract_pdf_subtask()
       → translate_blocks_subtask()
       → customize_tone_subtask()
       → reconstruct_pdf_subtask()
       → Update DB with results
```

**Resources:**
- Celery documentation
- Task chains & signatures
- Flower documentation

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Pipeline tested end-to-end
- ✅ Error handling verified
- ✅ Monitoring working
- ✅ Ready for Story 2.5

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
