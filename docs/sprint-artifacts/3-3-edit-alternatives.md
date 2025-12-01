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
- [ ] Click-to-edit on translated text
- [ ] Inline text editor
- [ ] Save/cancel options
- [ ] Real-time preview in review panel

### AC 3.3.2: Alternatives ✅
- [ ] Generate 2-3 alternative translations
- [ ] Show via Claude API
- [ ] Quick-select buttons
- [ ] Each alternative editable

### AC 3.3.3: Re-translation ✅
- [ ] Re-translate edited text
- [ ] Apply custom tone to re-translation
- [ ] Compare with original translation
- [ ] Keep best version

### AC 3.3.4: In-Memory Tracking ✅
- [ ] Track all user edits in Zustand store
- [ ] Distinguish original vs edited
- [ ] Persist edits until download
- [ ] Clear edits option

### AC 3.3.5: Integration ✅
- [ ] Edits reflected in final PDF
- [ ] Works with tone customization
- [ ] Non-destructive (original preserved)
- [ ] Edits visible in review panel

---

## Tasks & Subtasks

### Task 1: Create EditPanel Component
- [ ] Design edit interface
- [ ] Inline text editor
- [ ] Save/cancel buttons
- [ ] Character limit indicator
- [ ] Keyboard shortcuts

**Estimated Time:** 1.5 hours

### Task 2: Implement Alternatives Generation
- [ ] Create get_alternatives() endpoint
- [ ] Call Claude to generate options
- [ ] Show 2-3 alternatives
- [ ] Add quick-select buttons
- [ ] Cache alternatives

**Estimated Time:** 1.5 hours

### Task 3: Build Re-translation Logic
- [ ] Create re_translate endpoint
- [ ] Support custom tone parameter
- [ ] Apply tone to edited text
- [ ] Compare with original
- [ ] Store best version

**Estimated Time:** 1.5 hours

### Task 4: Add Edit Tracking
- [ ] Create edit tracker in Zustand
- [ ] Track block_id → edited_text
- [ ] Mark edited blocks visually
- [ ] Persist across sessions
- [ ] Clear all edits button

**Estimated Time:** 1 hour

### Task 5: Integrate with Review Panel
- [ ] Show edit indicators
- [ ] Click to edit
- [ ] Live preview of edits
- [ ] Sync edits with API
- [ ] Handle conflicts

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

**Current:** backlog  
**Last Updated:** 2025-11-15  
