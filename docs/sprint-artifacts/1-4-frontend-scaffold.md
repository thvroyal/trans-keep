# Story 1.4: Frontend Scaffold & shadcn/ui Setup

**Story Key:** 1-4-frontend-scaffold  
**Epic:** 1 - Setup & Scaffolding  
**Week:** Week 1 (Dec 2-6)  
**Duration:** 1 day  
**Owner:** Frontend Developer  
**Status:** ready-for-dev  

---

## Overview

Set up frontend application structure with shadcn/ui components, React Router for navigation, Zustand for state management, and TransKeep's custom design system (Figma-inspired).

---

## Acceptance Criteria

### AC 1.4.1: shadcn/ui Components Installed ✅
- [ ] shadcn/ui CLI initialized
- [ ] Button, Card, Input, Spinner, Dialog components added
- [ ] Tailwind CSS configured for shadcn/ui
- [ ] Component library working with npm run dev

### AC 1.4.2: React Router Setup ✅
- [ ] React Router v6+ installed
- [ ] Routes defined: /, /upload, /processing, /review, /auth/callback
- [ ] Navigation between routes working
- [ ] Protected routes (authenticated users only)

### AC 1.4.3: Zustand State Management ✅
- [ ] Zustand store created
- [ ] User state (authenticated, profile)
- [ ] CurrentJob state (job_id, status, progress)
- [ ] Store persists to localStorage
- [ ] Devtools integration for debugging

### AC 1.4.4: Tailwind + Custom Palette ✅
- [ ] Tailwind CSS configured
- [ ] TransKeep color palette defined in tailwind.config.ts
- [ ] Spacing, typography standards applied
- [ ] Responsive design working (mobile-first)

### AC 1.4.5: Project Layout ✅
- [ ] Upload page (file drop zone)
- [ ] Processing page (status + progress)
- [ ] Review page (dual PDF viewer placeholder)
- [ ] 404 page
- [ ] All pages navigable and styled

---

## Tasks & Subtasks

### Task 1: Install shadcn/ui Components
- [ ] Run `npx shadcn-ui@latest init`
- [ ] Add components: Button, Card, Input, Spinner, Dialog, Progress
- [ ] Test components with demo UI
- [ ] Verify component library loads without errors

**Estimated Time:** 1 hour

### Task 2: Set Up React Router
- [ ] Install react-router-dom
- [ ] Create router configuration
- [ ] Define 5 main routes
- [ ] Implement ProtectedRoute component
- [ ] Test navigation between pages

**Estimated Time:** 1.5 hours

### Task 3: Create Zustand Store
- [ ] Create store with auth slice
- [ ] Create store with job slice
- [ ] Implement localStorage persistence
- [ ] Add Zustand devtools
- [ ] Test store with console logs

**Estimated Time:** 1.5 hours

### Task 4: Configure Tailwind & Design System
- [ ] Create tailwind.config.ts with TransKeep palette
- [ ] Define color scales (primary, secondary, success, error, warning)
- [ ] Define typography (fonts, sizes, weights)
- [ ] Create globals.css with custom utilities
- [ ] Test responsive breakpoints

**Estimated Time:** 1.5 hours

### Task 5: Build Page Components
- [ ] Create UploadPage component
- [ ] Create ProcessingPage component
- [ ] Create ReviewPage component (placeholder)
- [ ] Create NotFoundPage component
- [ ] Create layout/header component
- [ ] Style all pages with Tailwind

**Estimated Time:** 2.5 hours

### Task 6: Test & Polish
- [ ] Test all routes work
- [ ] Test state persistence
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Test with `npm run build`
- [ ] Check lighthouse score

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- TransKeep color palette: Premium, modern aesthetic inspired by Figma
- All pages must be responsive (mobile-first approach)
- Use Zustand hooks instead of Redux for simplicity
- shadcn/ui provides pre-built, accessible components
- Tailwind utilities should be consistent across the app

**Design System:**
- Primary: Brand color (to be confirmed)
- Secondary: Accent color
- Surface: Background colors
- Elevated: Card backgrounds

**Resources:**
- docs/ux-design-specification.md (Design inspiration)
- shadcn/ui documentation
- React Router documentation
- Zustand documentation

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ All routes working and styled
- ✅ State management working
- ✅ Responsive design verified
- ✅ Build successful
- ✅ Ready for Story 1.5

---

## File List

**New Files:**
- [ ] frontend/src/router.tsx
- [ ] frontend/src/store/appStore.ts
- [ ] frontend/src/hooks/useAppStore.ts
- [ ] frontend/src/pages/UploadPage.tsx
- [ ] frontend/src/pages/ProcessingPage.tsx
- [ ] frontend/src/pages/ReviewPage.tsx
- [ ] frontend/src/pages/NotFoundPage.tsx
- [ ] frontend/src/components/Layout.tsx
- [ ] frontend/src/components/Header.tsx
- [ ] frontend/tailwind.config.ts
- [ ] frontend/src/globals.css

---

## Dev Agent Record

### Debug Log
*To be filled in during development*

### Completion Notes
*To be filled in after story completion*

---

## Status

**Current:** ready-for-dev  
**Last Updated:** 2025-11-15  

---

## Context Reference

- **Story Context File:** docs/sprint-artifacts/1-4-frontend-scaffold.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

