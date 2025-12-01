# Story 3.1: Side-by-Side Review Panel (Hero Component)

**Story Key:** 3-1-side-by-side-review  
**Epic:** 3 - UI Polish & Refinement  
**Week:** Week 3 (Dec 16-20)  
**Duration:** 2 days  
**Owner:** Frontend Developer  
**Status:** backlog  

---

## Overview

Implement the core hero feature: dual PDF viewer with synchronized scrolling and hover highlighting. Users can compare original and translated documents side-by-side without manual coordination.

---

## Acceptance Criteria

### AC 3.1.1: Dual PDF Rendering ✅
- [ ] Original PDF rendered on left (pdf.js)
- [ ] Translated PDF rendered on right (pdf.js)
- [ ] Both PDFs scroll independently
- [ ] Zoom controls for both

### AC 3.1.2: Synchronized Scrolling ✅
- [ ] Default: synchronized scrolling ON
- [ ] Toggle button to turn ON/OFF
- [ ] When ON: scrolling left syncs right and vice versa
- [ ] Smooth synchronization without lag

### AC 3.1.3: Hover Highlighting ✅
- [ ] Hover over text block → highlight both sides
- [ ] Block-level mapping visualized
- [ ] Visual feedback immediate
- [ ] Works on mobile (touch equivalent)

### AC 3.1.4: Responsive Design ✅
- [ ] Desktop: side-by-side (50/50 split)
- [ ] Tablet: side-by-side (stacked vertically)
- [ ] Mobile: tabs (switch between original/translated)
- [ ] All interactions remain smooth

### AC 3.1.5: Performance ✅
- [ ] 500-page PDF loads smoothly
- [ ] No lag during scrolling
- [ ] Highlighting instant (<50ms)
- [ ] Memory usage reasonable

---

## Tasks & Subtasks

### Task 1: Set Up pdf.js
- [ ] Install pdf.js library
- [ ] Create PDFViewer component
- [ ] Render PDFs with page controls
- [ ] Handle page-by-page rendering
- [ ] Test with various PDF sizes

**Estimated Time:** 2 hours

### Task 2: Implement Dual Viewer
- [ ] Create ReviewPanel component (main container)
- [ ] Render original PDF on left
- [ ] Render translated PDF on right
- [ ] Add page number synchronization
- [ ] Test both PDFs render correctly

**Estimated Time:** 2 hours

### Task 3: Add Synchronized Scrolling
- [ ] Create scroll position state (Zustand)
- [ ] Detect scroll events on left
- [ ] Update right panel scroll position
- [ ] Prevent infinite loops
- [ ] Add toggle button for on/off
- [ ] Test smooth synchronization

**Estimated Time:** 2 hours

### Task 4: Implement Hover Highlighting
- [ ] Create mapping of text blocks between PDFs
- [ ] On hover: highlight block in both PDFs
- [ ] Use visual effect (border or background)
- [ ] Make highlighting performant
- [ ] Test with various block sizes

**Estimated Time:** 2 hours

### Task 5: Make Responsive
- [ ] Create responsive layout component
- [ ] Desktop: dual column layout
- [ ] Tablet: adjust column widths
- [ ] Mobile: tab-based navigation
- [ ] Test on multiple screen sizes

**Estimated Time:** 1.5 hours

### Task 6: Performance Optimization
- [ ] Implement virtual scrolling for large PDFs
- [ ] Optimize re-renders
- [ ] Lazy load pages not in viewport
- [ ] Benchmark performance
- [ ] Optimize bundle size

**Estimated Time:** 2 hours

---

## Dev Notes

**Key Points:**
- pdf.js provides canvas-based PDF rendering
- Store scroll position in Zustand for cross-component communication
- Use debouncing for scroll events (100ms)
- Block mapping can be stored from extraction (Story 2.2)
- Virtual scrolling essential for large PDFs

**Architecture:**
```
ReviewPanel
├── PDFViewer (original, page 1-N)
├── PDFViewer (translated, page 1-N)
├── Sync Controller (scroll + highlight)
└── Responsive Handler
```

**Resources:**
- pdf.js documentation
- React virtualization libraries
- Performance optimization techniques

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Performance benchmarks met
- ✅ Responsive tested on multiple devices
- ✅ Hover highlighting working smoothly
- ✅ Ready for Story 3.2

---

## Status

**Current:** backlog  
**Last Updated:** 2025-11-15  
