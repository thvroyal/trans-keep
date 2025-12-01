# Story 2.3: DeepL Translation Integration

**Story Key:** 2-3-deepl-translation  
**Epic:** 2 - Core Translation Pipeline  
**Week:** Week 2 (Dec 9-13)  
**Duration:** 1.5 days  
**Owner:** Backend Developer  
**Status:** backlog  

---

## Overview

Integrate DeepL API for high-quality document translation. Implement batch translation with parallelization for performance and cost efficiency.

---

## Acceptance Criteria

### AC 2.3.1: DeepL API Integration ✅
- [ ] DeepL Python client installed and configured
- [ ] API key stored in environment variables
- [ ] Translation endpoint working with EN→JA, EN→VI, EN→ZH

### AC 2.3.2: Batch Translation ✅
- [ ] Implement batch processing (10 blocks per request)
- [ ] Reduce API calls and costs
- [ ] Handle variable batch sizes

### AC 2.3.3: Parallelization ✅
- [ ] Process multiple pages in parallel
- [ ] Use Celery worker pool
- [ ] Maintain cost budget (<$0.15 per job)

### AC 2.3.4: Error Handling ✅
- [ ] Handle API rate limiting with backoff
- [ ] Retry failed translations
- [ ] Graceful degradation if API unavailable

### AC 2.3.5: Integration ✅
- [ ] Integrated with Celery pipeline
- [ ] Receives extracted blocks from Story 2.2
- [ ] Returns translated blocks to database
- [ ] Ready for Story 2.4

---

## Tasks & Subtasks

### Task 1: Set Up DeepL Client
- [ ] Install deepl-python package
- [ ] Store API key in .env
- [ ] Create translation service module
- [ ] Test basic translation

**Estimated Time:** 1 hour

### Task 2: Implement Batch Translation
- [ ] Create batch_translate() function
- [ ] Group blocks into batches of 10
- [ ] Call DeepL API for each batch
- [ ] Optimize batch size for cost/speed

**Estimated Time:** 1.5 hours

### Task 3: Add Parallelization
- [ ] Create Celery tasks for page-level translation
- [ ] Use worker pool for parallel processing
- [ ] Orchestrate task flow (extract → translate)
- [ ] Monitor costs

**Estimated Time:** 2 hours

### Task 4: Implement Error Handling
- [ ] Catch rate limit errors
- [ ] Implement exponential backoff retry
- [ ] Log all API calls
- [ ] Handle timeout scenarios

**Estimated Time:** 1.5 hours

### Task 5: Integrate with Pipeline
- [ ] Connect to Story 2.2 extracted blocks
- [ ] Store translations in database
- [ ] Update translation status
- [ ] Handle partial failures

**Estimated Time:** 1.5 hours

### Task 6: Cost & Performance Testing
- [ ] Test with 10-page document
- [ ] Test with 100-page document
- [ ] Track API costs
- [ ] Verify quality of translation
- [ ] Benchmark execution time

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- DeepL free tier: 500,000 characters/month
- Pro tier: unlimited, pay as you go
- Batch 10 blocks per API call to reduce overhead
- Language codes: EN→JA, EN→VI, EN→ZH supported
- Store translation costs for billing

**Cost Estimation:**
```
Average document: 50,000 words → ~250,000 chars
Cost per document: $0.05 (Pro tier)
Budget: $0.15 per job allows 3 jobs
```

**Resources:**
- DeepL API documentation
- Celery task orchestration
- Budget tracking

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Cost benchmarks verified
- ✅ Error handling tested
- ✅ Integration working
- ✅ Ready for Story 2.4

---

## File List

**New Files:**
- [ ] backend/app/services/translation_service.py
- [ ] backend/app/tasks/translate_blocks.py
- [ ] backend/tests/test_translation.py

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
