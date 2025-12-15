# Story 3.3: Edit & Alternatives Workflow

**Story Key:** 3-3-edit-alternatives  
**Epic:** 3 - UI Polish & Refinement  
**Week:** Week 3 (Dec 16-20)  
**Duration:** 1.5 days  
**Owner:** Frontend + Backend Developer  
**Status:** backlog  

---

## Overview

Let users edit translated text, get AI-generated alternatives, and re-translate edited sections with custom tone.

---

## Acceptance Criteria

### AC 3.3.1: Edit Panel ✅
- [x] Click-to-edit on translated text
- [x] Inline text editor
- [x] Save/cancel options
- [x] Real-time preview in review panel

### AC 3.3.2: Alternatives ✅
- [x] Generate 2-3 alternative translations
- [x] Show via Claude API
- [x] Quick-select buttons
- [x] Each alternative editable

### AC 3.3.3: Re-translation ✅
- [x] Re-translate edited text
- [x] Apply custom tone to re-translation
- [x] Compare with original translation
- [x] Keep best version

### AC 3.3.4: In-Memory Tracking ✅
- [x] Track all user edits in Zustand store
- [x] Distinguish original vs edited
- [x] Persist edits until download
- [x] Clear edits option

### AC 3.3.5: Integration ✅
- [ ] Edits reflected in final PDF (Note: Requires PDF reconstruction with edits - to be implemented)
- [x] Works with tone customization
- [x] Non-destructive (original preserved)
- [x] Edits visible in review panel

---

## Tasks & Subtasks

### Task 1: Create EditPanel Component
- [x] Design edit interface
- [x] Inline text editor
- [x] Save/cancel buttons
- [x] Character limit indicator
- [x] Keyboard shortcuts

**Estimated Time:** 1.5 hours

### Task 2: Implement Alternatives Generation
- [x] Create get_alternatives() endpoint
- [x] Call Claude to generate options
- [x] Show 2-3 alternatives
- [x] Add quick-select buttons
- [ ] Cache alternatives (Note: Can be added as optimization)

**Estimated Time:** 1.5 hours

### Task 3: Build Re-translation Logic
- [x] Create re_translate endpoint
- [x] Support custom tone parameter
- [x] Apply tone to edited text
- [x] Compare with original
- [x] Store best version

**Estimated Time:** 1.5 hours

### Task 4: Add Edit Tracking
- [x] Create edit tracker in Zustand
- [x] Track block_id → edited_text
- [x] Mark edited blocks visually
- [x] Persist across sessions
- [x] Clear all edits button

**Estimated Time:** 1 hour

### Task 5: Integrate with Review Panel
- [x] Show edit indicators
- [x] Click to edit
- [x] Live preview of edits
- [x] Sync edits with API
- [x] Handle conflicts

**Estimated Time:** 1.5 hours

### Task 6: Testing & Polish
- [ ] Test edit flow end-to-end
- [ ] Test alternatives quality
- [ ] Test re-translation accuracy
- [ ] Performance with many edits
- [ ] Cross-browser testing

**Estimated Time:** 1.5 hours

---

## Status

**Current:** review  
**Last Updated:** 2025-12-09

---

## Dev Agent Record

### Debug Log
- Created EditPanel component with inline editor, save/cancel, character limit, and keyboard shortcuts (Ctrl+S, Esc)
- Implemented AlternativesService using Claude API to generate 2-5 alternative translations
- Created re-translation endpoint that uses ToneService to re-translate with custom tone
- Built edit tracking in Zustand store with persistence to localStorage
- Integrated BlocksPanel with ReviewPage showing edit indicators and click-to-edit functionality
- Added GET /api/v1/translation/{job_id}/blocks endpoint to retrieve blocks for editing
- Added POST /api/v1/alternatives endpoint for generating alternatives
- Added POST /api/v1/retranslate endpoint for re-translating with tone

### Completion Notes
**Implementation Summary:**
- ✅ EditPanel component with full editing capabilities
- ✅ Alternatives generation via Claude API
- ✅ Re-translation with custom tone support
- ✅ Edit tracking in Zustand with persistence
- ✅ BlocksPanel integrated with ReviewPage
- ✅ All backend endpoints implemented
- ⚠️ PDF reconstruction with edits not yet implemented (requires PDF rebuild on download - separate task)

**Key Files Created/Modified:**
- `frontend/src/components/EditPanel.tsx` - Main edit component
- `frontend/src/components/BlocksPanel.tsx` - Blocks list with edit functionality
- `frontend/src/components/ui/textarea.tsx` - Textarea component
- `frontend/src/store/editSlice.ts` - Edit tracking store
- `frontend/src/pages/ReviewPage.tsx` - Integrated blocks panel
- `backend/app/services/alternatives_service.py` - Alternatives generation service
- `backend/app/routers/translation.py` - Added alternatives, retranslate, and blocks endpoints
- `backend/app/schemas/translation.py` - Added request/response schemas

**Follow-ups:**
- PDF reconstruction with edits needs to be implemented to fully satisfy AC 3.3.5
- Consider adding alternatives caching for performance
- Add comprehensive tests for edit flow

---

## File List

### Frontend
- `frontend/src/components/EditPanel.tsx` (new)
- `frontend/src/components/BlocksPanel.tsx` (new)
- `frontend/src/components/ui/textarea.tsx` (new)
- `frontend/src/store/editSlice.ts` (new)
- `frontend/src/pages/ReviewPage.tsx` (modified)

### Backend
- `backend/app/services/alternatives_service.py` (new)
- `backend/app/routers/translation.py` (modified)
- `backend/app/schemas/translation.py` (modified)

---

## Change Log

### 2025-12-09
- Implemented edit and alternatives workflow (Story 3.3)
- Created EditPanel component with inline editing, alternatives, and re-translation
- Added edit tracking in Zustand store with persistence
- Integrated blocks panel with ReviewPage
- Added backend endpoints for alternatives, re-translation, and blocks retrieval
- Note: PDF reconstruction with edits pending (requires separate implementation)  
