# Story 3.2: Tone Customization UI & Logic

**Story Key:** 3-2-tone-customization  
**Epic:** 3 - UI Polish & Refinement  
**Week:** Week 3 (Dec 16-20)  
**Duration:** 1.5 days  
**Owner:** Frontend + Backend Developer  
**Status:** backlog  

---

## Overview

Let users customize translation tone (professional, casual, technical, etc.) before translation or apply to completed translation using Claude Haiku. Show before/after comparison.

---

## Acceptance Criteria

### AC 3.2.1: Tone UI ✅
- [ ] ToneSelector component with 5 presets
- [ ] Custom tone input field
- [ ] Visual preview of tone
- [ ] Apply tone button

### AC 3.2.2: Tone Options ✅
- [ ] Professional (formal business)
- [ ] Casual (friendly, conversational)
- [ ] Technical (for documentation)
- [ ] Creative (for marketing)
- [ ] Custom (user-defined)

### AC 3.2.3: Claude Integration ✅
- [ ] Claude API re-translates with tone
- [ ] Shows before/after comparison
- [ ] Visual diff highlighting
- [ ] Cost tracking (~$0.048/doc)

### AC 3.2.4: User Experience ✅
- [ ] Apply tone instantly
- [ ] Visual feedback during processing
- [ ] Can select tone before upload (recommended)
- [ ] Can apply after translation
- [ ] Can preview without applying

### AC 3.2.5: Integration ✅
- [ ] Integrated with Celery pipeline
- [ ] Works with review panel
- [ ] Editable after tone applied
- [ ] Cost visible to user

---

## Tasks & Subtasks

### Task 1: Create ToneSelector Component
- [ ] Design tone preset buttons
- [ ] Create custom input field
- [ ] Show selected tone
- [ ] Add descriptions for each tone
- [ ] Make responsive

**Estimated Time:** 1 hour

### Task 2: Implement Backend Tone Service
- [ ] Create tone_service.py
- [ ] Configure Claude API client
- [ ] Implement re-translation logic
- [ ] Handle streaming responses
- [ ] Track API costs

**Estimated Time:** 1.5 hours

### Task 3: Build Before/After UI
- [ ] Create comparison view component
- [ ] Show original translation
- [ ] Show tone-customized version
- [ ] Highlight differences
- [ ] Add accept/reject buttons

**Estimated Time:** 1.5 hours

### Task 4: Integrate with Pipeline
- [ ] Add tone_customization task to Celery
- [ ] Support pre-upload tone selection
- [ ] Support post-translation tone application
- [ ] Update status tracking
- [ ] Handle tone API failures

**Estimated Time:** 1.5 hours

### Task 5: Implement Cost Tracking
- [ ] Track Claude API usage
- [ ] Display cost to user
- [ ] Add cost warning if exceeds budget
- [ ] Store cost in translation record
- [ ] Show cumulative cost

**Estimated Time:** 1 hour

### Task 6: Testing & Polish
- [ ] Test tone application
- [ ] Test before/after comparison
- [ ] Test cost tracking
- [ ] Performance test with large documents
- [ ] Cross-browser testing

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- Claude Haiku: $0.80 per million input tokens, $4 per million output tokens
- Pre-defined tone prompts for consistent results
- Cache tone results in Redis to avoid duplicate Claude calls
- Show cost estimate before applying tone
- Tone is optional - translation works without it

**Tone Prompts:**
```
Professional: "Re-write this in formal business language..."
Casual: "Re-write this in friendly, conversational tone..."
Technical: "Simplify this for technical audience..."
Creative: "Re-write this for marketing impact..."
```

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
