# Story 1.3: Google OAuth Integration

**Story Key:** 1-3-google-oauth-integration  
**Epic:** 1 - Setup & Scaffolding  
**Week:** Week 1 (Dec 2-6)  
**Duration:** 1 day  
**Owner:** Backend Developer  
**Status:** ready-for-dev  

---

## Overview

Implement Google OAuth 2.0 authentication using better-auth library on both backend and frontend. Users can sign in with Google, receive JWT tokens, and access protected endpoints.

---

## Acceptance Criteria

### AC 1.3.1: Google OAuth Credentials ✅
- [ ] Google OAuth app registered in Google Cloud Console
- [ ] Client ID and Client Secret obtained
- [ ] Redirect URI configured: http://localhost:3000/callback
- [ ] Credentials stored in .env files

### AC 1.3.2: Backend better-auth Setup ✅
- [ ] better-auth installed and configured
- [ ] Google provider configured
- [ ] JWT token generation working
- [ ] Token refresh logic implemented

### AC 1.3.3: Frontend OAuth Flow ✅
- [ ] better-auth React hook installed
- [ ] Sign-in button implemented
- [ ] Callback page handles OAuth redirect
- [ ] Token stored securely (httpOnly cookie)

### AC 1.3.4: Protected Endpoints ✅
- [ ] Middleware verifies JWT tokens
- [ ] GET /api/v1/me returns user info
- [ ] Unauthorized endpoints return 401
- [ ] Token expiration handled

### AC 1.3.5: Sign Out & Session Management ✅
- [ ] Sign out clears token
- [ ] Session persists on page reload
- [ ] Token refresh works automatically
- [ ] No token exposed in localStorage

---

## Tasks & Subtasks

### Task 1: Register Google OAuth App
- [ ] Go to Google Cloud Console
- [ ] Create new OAuth 2.0 Consent Screen
- [ ] Configure OAuth 2.0 Client ID (Web Application)
- [ ] Set Authorized redirect URIs
- [ ] Copy Client ID and Client Secret
- [ ] Store in backend/.env

**Estimated Time:** 30 minutes

### Task 2: Configure better-auth Backend
- [ ] Install better-auth and google provider
- [ ] Create auth configuration
- [ ] Set up JWT secret and expiration
- [ ] Implement /auth/google/callback endpoint
- [ ] Implement /auth/logout endpoint
- [ ] Test OAuth flow locally

**Estimated Time:** 2 hours

### Task 3: Implement Frontend OAuth
- [ ] Install @better-auth/react
- [ ] Create useAuth hook
- [ ] Create SignIn button component
- [ ] Create callback page (/auth/callback)
- [ ] Store token in httpOnly cookie
- [ ] Test sign-in flow

**Estimated Time:** 2 hours

### Task 4: Add Authentication Middleware
- [ ] Create JWT verification middleware
- [ ] Protect /api/v1/* endpoints
- [ ] Implement GET /api/v1/me endpoint
- [ ] Add user info to request context
- [ ] Test with curl requests

**Estimated Time:** 1.5 hours

### Task 5: Implement Session Persistence
- [ ] Check for existing token on app load
- [ ] Refresh token if expired
- [ ] Handle token expiration gracefully
- [ ] Redirect to sign-in if needed
- [ ] Test persistence across sessions

**Estimated Time:** 1 hour

### Task 6: Write Tests
- [ ] Test Google OAuth flow
- [ ] Test token generation and validation
- [ ] Test protected endpoints
- [ ] Test sign-out flow
- [ ] Test session persistence

**Estimated Time:** 1.5 hours

---

## Dev Notes

**Key Points:**
- better-auth handles token refresh automatically
- Use httpOnly cookies for security (no XSS vulnerability)
- JWT tokens valid for 24 hours (configurable)
- User info stored in database on first login
- All OAuth operations must use HTTPS in production

**Resources:**
- docs/architecture.md (Section 3.1: Authentication)
- better-auth documentation
- Google Cloud Console docs

---

## Definition of Done

- ✅ All 5 acceptance criteria met
- ✅ All 6 tasks completed
- ✅ Tests passing
- ✅ Can sign in with Google locally
- ✅ User session persists
- ✅ Ready for Story 1.4

---

## File List

**New Files:**
- [ ] backend/app/routers/auth.py
- [ ] backend/app/schemas/auth.py
- [ ] frontend/src/hooks/useAuth.ts
- [ ] frontend/src/pages/AuthCallback.tsx
- [ ] frontend/src/components/SignIn.tsx
- [ ] backend/tests/test_auth.py

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

- **Story Context File:** docs/sprint-artifacts/1-3-google-oauth-integration.context.xml
- **Architecture Reference:** docs/architecture.md
- **Sprint Plan:** docs/sprint-plan.md

