# TransKeep - Epic Breakdown

**Author:** Roy  
**Date:** December 14, 2025  
**Project Level:** Enterprise  
**Target Scale:** MVP to Enterprise

---

## Overview

This document provides the complete epic and story breakdown for TransKeep, decomposing the requirements from the [PRD](./PRD.md) into implementable stories.

**Living Document Notice:** This is the initial version. It will be updated after UX Design and Architecture workflows add interaction and technical details to stories.

---

## Epic Summary

**Epic 1: Foundation & User Authentication** - Establishes infrastructure, database, authentication, and subscription management (FR1-10)

**Epic 2: Document Upload & Translation Pipeline** - Complete translation workflow from upload through processing (FR11-40)

**Epic 3: Review & Refinement Experience** - Side-by-side review, tone customization, and editing capabilities (FR41-70)

**Epic 4: Download & System Management** - Download functionality, session management, error handling, and system operations (FR71-100)

---

## Functional Requirements Inventory

**Total: 100 Functional Requirements**

### FR1-10: User Account & Authentication
- **FR1:** Users can create an account via Google OAuth sign-in (no email/password signup)
- **FR2:** Users remain logged in across browser sessions (persistent authentication)
- **FR3:** Users can log out at any time
- **FR4:** System tracks whether user is on free tier or paid subscription
- **FR5:** Free tier users see a counter: "X of 2 documents used this month"
- **FR6:** When free tier limit reached, user sees upgrade prompt (not a hard block, just messaging)
- **FR7:** Paid subscribers have unlimited document uploads and translations
- **FR8:** System displays current subscription status and renewal date for paid users
- **FR9:** Users can cancel subscription anytime
- **FR10:** System sends email confirmation for subscription changes

### FR11-20: Document Upload & File Handling
- **FR11:** Users can drag-drop PDF files onto upload area
- **FR12:** Users can click to browse and select PDF files
- **FR13:** System validates file is actually a PDF (not other formats disguised as PDF)
- **FR14:** System accepts files up to 100MB in size
- **FR15:** System rejects files larger than 100MB with clear error message
- **FR16:** System displays upload progress with file size and estimated time
- **FR17:** System auto-detects if PDF is digital or scanned (uses OCR for scanned)
- **FR18:** System displays warning for very large files (50MB+) with estimated processing time
- **FR19:** System supports simultaneous uploads (user can prepare next document while one is processing)
- **FR20:** System queues and processes uploads sequentially if multiple attempted simultaneously

### FR21-30: Language Selection & Source Detection
- **FR21:** Users select target language from dropdown: Japanese, Vietnamese
- **FR22:** System auto-detects source language (English detection for MVP)
- **FR23:** If source language is not English, system warns user (MVP only supports English source)
- **FR24:** Users can override source language detection if needed
- **FR25:** System displays language pair clearly: "English → Japanese"
- **FR26:** System validates language pair is supported before translation
- **FR27:** For future expansion, system stores selected language in user session
- **FR28:** System displays supported language pairs clearly in UI

### FR31-40: Translation Processing & Status
- **FR31:** System begins translation after user selects target language and confirms
- **FR32:** System displays progress indicator while translating (% complete or "processing...")
- **FR33:** For documents with multiple pages, system shows page-by-page progress
- **FR34:** System processes large documents asynchronously (doesn't block UI)
- **FR35:** System completes translation within 90 seconds for typical 100-page document
- **FR36:** If translation fails (API error, timeout, etc.), system displays user-friendly error and options to retry
- **FR37:** System stores temporary translation results in memory/session (not persistent database for MVP)
- **FR38:** System auto-deletes processed files 24 hours after creation (cleanup job)
- **FR39:** If user leaves during processing, session is preserved for 30 minutes to resume
- **FR40:** System displays estimated time remaining during processing

### FR41-50: Side-by-Side Review Interface
- **FR41:** After translation completes, system displays dual-panel interface: left (original) and right (translated)
- **FR42:** Both PDF panels render with full formatting preserved (images, tables, text styling)
- **FR43:** Users can scroll within each panel independently or scroll together (sync toggle)
- **FR44:** Default: Synchronized scrolling (both panels move together for easy comparison)
- **FR45:** Users can toggle synchronized scrolling on/off
- **FR46:** When user hovers over any text block in original, corresponding block in translation highlights (and vice versa)
- **FR47:** Highlighting is block-level: paragraphs, table cells, captions, headers
- **FR48:** Highlighting uses color accent (not intrusive, maintains readability)
- **FR49:** Users can zoom in/out on both panels (maintains sync)
- **FR50:** Mobile/tablet: Side-by-side stacks vertically on small screens, with tab toggle between original/translated

### FR51-60: Tone Customization
- **FR51:** After review, users access "Tone" panel/modal
- **FR52:** Tone panel displays 5 predefined tone presets: Formal, Casual, Technical, Creative, Academic
- **FR53:** Users can click any preset to apply it
- **FR54:** Applying tone re-translates the document with that style (takes 15-30 seconds)
- **FR55:** Users can see new translation immediately after tone applied (same dual-panel view)
- **FR56:** Users can compare: original tone vs new tone side-by-side (show before/after)
- **FR57:** Users can enter custom tone description: free-text field like "poetic and romantic" or "funny and casual"
- **FR58:** System applies custom tone via Claude Haiku (re-translates with that description)
- **FR59:** Users can switch between tone options multiple times (no limits)
- **FR60:** System caches tone variations to avoid re-translating if user applies same tone twice

### FR61-70: Edit & Alternatives Workflow
- **FR61:** Users can click any text block in the translated version to edit
- **FR62:** Clicking opens an edit panel with that block's translation pre-filled
- **FR63:** Users can type in the edit field to modify the translation
- **FR64:** Users can see 2-3 alternative phrasings for that block (generated by Claude)
- **FR65:** Users can click any alternative to select it (replaces current translation)
- **FR66:** Clicking "Apply" saves the edit and updates the translated PDF view
- **FR67:** Users can re-translate with a custom tone: "Translate this with [tone description]"
- **FR68:** System applies tone-specific re-translation and shows result immediately
- **FR69:** Edits are tracked in session (not permanent until download)
- **FR70:** Users can undo edits using browser back or explicit "Undo" button

### FR71-80: Download & Export
- **FR71:** After user finishes reviewing/editing, they click "Download Translated PDF"
- **FR72:** System generates final PDF with all edits and tone customizations applied
- **FR73:** Final PDF preserves original formatting: fonts, spacing, images, layout
- **FR74:** System displays download progress (usually instant for small files, 5-10 sec for large)
- **FR75:** Downloaded file is named: "{original_filename}_translated_{target_language}.pdf"
- **FR76:** Users can download the same translation multiple times without re-processing
- **FR77:** Users receive confirmation when download completes
- **FR78:** Optional future: Users can download original + translated as bilingual PDF (Phase 2)
- **FR79:** Optional future: Users can export as DOCX or other formats (Phase 2)
- **FR80:** System includes TransKeep branding/watermark (optional, may remove for paid tier)

### FR81-90: Session & State Management
- **FR81:** All user work (edits, tone customizations) is session-based
- **FR82:** User session persists for 12 hours of inactivity
- **FR83:** After session expires, user must re-upload to continue (for MVP simplicity)
- **FR84:** If user closes browser, all unsaved work is lost (warning before closing)
- **FR85:** Users cannot save "projects" or history in MVP (Phase 2 feature)
- **FR86:** Each translation is independent (no linking between documents)
- **FR87:** System does not retain copies of user's documents after download
- **FR88:** User data is not shared between users (multi-tenant isolation)
- **FR89:** System logs basic metrics (upload count, successful translations, errors) for analytics
- **FR90:** User can delete their account anytime (deletes all associated data)

### FR91-100: Error Handling & Edge Cases
- **FR91:** If translation API fails, system displays: "Translation failed. Please try again."
- **FR92:** User can retry translation from failure point (reload original, not re-upload)
- **FR93:** If PDF is corrupted/invalid, system displays: "This PDF appears to be corrupted. Please check and try another file."
- **FR94:** If PDF is scanned (no selectable text), system notifies user: "This appears to be a scanned PDF. Processing may take longer for OCR."
- **FR95:** If OCR fails on scanned PDF, system displays: "Could not extract text from this scanned PDF. Please ensure image quality is good."
- **FR96:** If user's internet disconnects during upload/translation, system stores state and allows resume on reconnection
- **FR97:** If user runs out of free tier limit mid-translation, system completes current translation and prompts upgrade for next
- **FR98:** All error messages include support contact or help link
- **FR99:** System logs all errors for monitoring and debugging
- **FR100:** System displays timeout messages if any operation exceeds expected time by 30%

---

## FR Coverage Map

**Epic 1: Foundation & User Authentication**
- FR1-10: User Account & Authentication (all 10 FRs)

**Epic 2: Document Upload & Translation Pipeline**
- FR11-20: Document Upload & File Handling (all 10 FRs)
- FR21-30: Language Selection & Source Detection (all 8 FRs)
- FR31-40: Translation Processing & Status (all 10 FRs)

**Epic 3: Review & Refinement Experience**
- FR41-50: Side-by-Side Review Interface (all 10 FRs)
- FR51-60: Tone Customization (all 10 FRs)
- FR61-70: Edit & Alternatives Workflow (all 10 FRs)

**Epic 4: Download & System Management**
- FR71-80: Download & Export (all 10 FRs)
- FR81-90: Session & State Management (all 10 FRs)
- FR91-100: Error Handling & Edge Cases (all 10 FRs)

**Total Coverage:** 100/100 FRs (100%)

---

## Epic 1: Foundation & User Authentication

**Goal:** Establish the foundational infrastructure, database schema, authentication system, and subscription management that enables all subsequent features. This epic creates the multi-tenant architecture foundation and user account capabilities.

**Value:** Without this foundation, no user can access the system, and no translation work can be tracked or managed. This epic delivers the first deployable functionality: users can sign in and see their account status.

**FR Coverage:** FR1-10 (User Account & Authentication)

---

### Story 1.1: Project Infrastructure Setup

**As a** developer,  
**I want** a complete development environment with all core frameworks and infrastructure initialized,  
**So that** I can begin implementing features with a solid foundation.

**Acceptance Criteria:**

**Given** a new project repository  
**When** I run the setup commands  
**Then** the following are initialized:
- Frontend: React 18 + TypeScript + Vite project structure
- Backend: FastAPI + Python 3.11 project with `pyproject.toml` and `uv` package manager
- Docker Compose configuration for local development (PostgreSQL, Redis, Jaeger)
- CI/CD pipeline (GitHub Actions) with basic workflow
- Project structure follows best practices (separate frontend/backend directories)

**And** all core dependencies are installed and verified  
**And** `.env.example` file exists with required environment variables documented  
**And** README.md includes setup instructions

**Prerequisites:** None (this is the first story)

**Technical Notes:**
- Use `pnpm create vite` for frontend scaffold
- Use FastAPI template with async support
- Docker Compose should include: postgres:15, redis:7, jaeger (for OpenTelemetry)
- CI/CD should run linting and basic tests
- Architecture workflow will add detailed technical decisions

**FR Coverage:** Infrastructure foundation (enables all FRs)

---

### Story 1.2: Database Schema & Multi-Tenant Foundation

**As a** system architect,  
**I want** a PostgreSQL database schema with multi-tenant isolation and user management tables,  
**So that** user data is properly isolated and subscription tracking works correctly.

**Acceptance Criteria:**

**Given** a fresh PostgreSQL database  
**When** I run database migrations  
**Then** the following tables are created:
- `users` table with: id (UUID), email, google_id, subscription_tier (enum: free, paid), created_at, updated_at
- `subscriptions` table with: id, user_id (FK), status (active, cancelled), renewal_date, cancelled_at
- `translation_jobs` table with: id (UUID), user_id (FK), status, file_path, created_at, expires_at
- All tables include proper indexes on foreign keys and frequently queried columns
- Multi-tenant isolation enforced at application level (user_id filtering on all queries)

**And** Alembic migrations are set up and working  
**And** Database connection pooling is configured (SQLAlchemy with async support)  
**And** Seed data script exists for local development (test users)

**Prerequisites:** Story 1.1 (Project Infrastructure Setup)

**Technical Notes:**
- Use SQLAlchemy ORM with async support
- Use UUIDs for primary keys (better for multi-tenant)
- Subscription tier enum: `free`, `paid`
- All queries must filter by `user_id` to enforce isolation
- Architecture workflow will refine schema design

**FR Coverage:** FR4 (System tracks subscription tier), FR88 (Multi-tenant isolation)

---

### Story 1.3: Google OAuth Authentication Integration

**As a** user,  
**I want** to sign in with my Google account using OAuth,  
**So that** I can access TransKeep without creating a separate password.

**Acceptance Criteria:**

**Given** a user visits the application  
**When** they click "Sign in with Google"  
**Then** they are redirected to Google OAuth consent screen  
**And** after consenting, they are redirected back to the application  
**And** a user account is created in the database (if first time) or existing account is retrieved  
**And** a secure session is established with JWT token stored in httpOnly cookie  
**And** the user is redirected to the main application page

**Given** a user is already signed in  
**When** they return to the application  
**Then** they remain authenticated (session persists across browser sessions)  
**And** their user information is available to the application

**Given** a user wants to sign out  
**When** they click "Sign out"  
**Then** their session is invalidated  
**And** they are redirected to the sign-in page  
**And** all session data is cleared

**Prerequisites:** Story 1.2 (Database Schema)

**Technical Notes:**
- Use `better-auth` library for OAuth integration
- Backend: better-auth FastAPI integration with Google provider
- Frontend: better-auth React hooks for authentication state
- JWT tokens with 7-day expiration for persistent sessions
- Store Google user ID in database for account linking
- Handle OAuth callback with CSRF protection
- Architecture workflow will specify security details

**FR Coverage:** FR1 (Google OAuth sign-in), FR2 (Persistent authentication), FR3 (Log out)

---

### Story 1.4: Subscription Tier Management & Display

**As a** user,  
**I want** to see my current subscription status and document usage,  
**So that** I understand my account limits and can upgrade when needed.

**Acceptance Criteria:**

**Given** a free tier user  
**When** they view their account or upload page  
**Then** they see a counter: "X of 2 documents used this month"  
**And** the counter increments after each document upload  
**And** the counter resets at the start of each calendar month

**Given** a free tier user who has used 2 documents  
**When** they attempt to upload a third document or view their account  
**Then** they see an upgrade prompt: "You've used your 2 free documents this month. Upgrade to unlimited translations."  
**And** the prompt includes a link to subscription management  
**And** the prompt is informational (not a hard block - they can still see the interface)

**Given** a paid subscriber  
**When** they view their account  
**Then** they see: "Unlimited translations" status  
**And** their subscription renewal date is displayed  
**And** they can see subscription management options

**Given** any user  
**When** they view account settings  
**Then** their current subscription tier is clearly displayed  
**And** subscription management actions are available (upgrade, cancel)

**Prerequisites:** Story 1.3 (Google OAuth Authentication)

**Technical Notes:**
- Track document count per user per month in database
- Use PostgreSQL date functions for month boundary detection
- Subscription status endpoint: `GET /api/v1/user/subscription`
- Document count endpoint: `GET /api/v1/user/usage`
- Frontend: Display subscription status in header/navbar
- Server-side enforcement of limits (not just frontend)
- Architecture workflow will specify subscription service design

**FR Coverage:** FR4 (Track subscription tier), FR5 (Free tier counter), FR6 (Upgrade prompt), FR7 (Paid unlimited), FR8 (Subscription status display)

---

### Story 1.5: Subscription Management & Email Notifications

**As a** user,  
**I want** to manage my subscription (upgrade, cancel) and receive email confirmations,  
**So that** I have control over my account and clear records of changes.

**Acceptance Criteria:**

**Given** a free tier user  
**When** they click "Upgrade to Paid"  
**Then** they are taken to subscription management page  
**And** they can select a subscription plan (pricing TBD)  
**And** payment processing is integrated (Stripe or similar)  
**And** after successful payment, their subscription tier is updated to "paid"  
**And** an email confirmation is sent with subscription details

**Given** a paid subscriber  
**When** they click "Cancel Subscription"  
**Then** they see a confirmation dialog  
**And** after confirming, their subscription status changes to "cancelled"  
**And** they retain access until the end of the current billing period  
**And** an email confirmation is sent with cancellation details and renewal date

**Given** any subscription change  
**When** the change is processed  
**Then** an email is sent to the user's Google account email  
**And** the email includes: change type, effective date, next renewal date (if applicable)  
**And** the email is sent within 5 minutes of the change

**Prerequisites:** Story 1.4 (Subscription Tier Management)

**Technical Notes:**
- Integrate Stripe or similar payment processor
- Webhook handler for subscription events (payment success, cancellation)
- Email service integration (SendGrid, AWS SES, or similar)
- Email templates for: subscription activated, cancelled, renewal reminder
- Subscription changes logged in database for audit trail
- Architecture workflow will specify payment integration details

**FR Coverage:** FR9 (Cancel subscription), FR10 (Email confirmation)

---

## Epic 2: Document Upload & Translation Pipeline

**Goal:** Enable users to upload PDF documents, select target languages, and process translations asynchronously with real-time status updates. This epic delivers the core translation workflow from file upload through completed translation ready for review.

**Value:** This is the core product capability - without this, users cannot translate documents. This epic delivers the primary value proposition: uploading a document and receiving a translated version.

**FR Coverage:** FR11-40 (Document Upload, Language Selection, Translation Processing)

---

### Story 2.1: PDF File Upload with Validation

**As a** user,  
**I want** to upload PDF files by dragging and dropping or browsing,  
**So that** I can translate my documents easily.

**Acceptance Criteria:**

**Given** a user is signed in  
**When** they visit the upload page  
**Then** they see a large drop zone (50%+ of screen) with drag-drop area  
**And** they see a "Browse Files" button for file selection  
**And** the interface clearly indicates PDF files are accepted

**Given** a user drags a file onto the drop zone or selects a file via browse  
**When** the file is a valid PDF  
**Then** the file is accepted  
**And** upload progress is displayed with: file name, file size, upload percentage, estimated time remaining  
**And** the file is uploaded in chunks (for large files)  
**And** upload completes successfully

**Given** a user attempts to upload a file  
**When** the file is not a PDF (e.g., .docx, .txt, disguised PDF)  
**Then** validation fails before upload starts  
**And** error message: "Please upload a PDF file. Other formats are not supported."  
**And** the file is rejected

**Given** a user attempts to upload a file  
**When** the file size exceeds 100MB  
**Then** validation fails  
**And** error message: "File size exceeds 100MB limit. Please use a smaller file."  
**And** the file is rejected

**Given** a user uploads a file between 50-100MB  
**When** the file is selected  
**Then** a warning is displayed: "Large file detected. Processing may take 2-3 minutes."  
**And** the user can proceed or cancel

**Prerequisites:** Story 1.3 (Google OAuth Authentication), Story 1.4 (Subscription Tier Management - for usage tracking)

**Technical Notes:**
- Frontend: React Dropzone component or custom drag-drop handler
- Backend: FastAPI multipart upload endpoint `POST /api/v1/upload`
- File validation: Check MIME type and file signature (not just extension)
- Chunked upload for files >10MB using resumable upload protocol
- Store uploaded file temporarily in S3 with unique UUID
- Create translation_job record in database with status "uploaded"
- Architecture workflow will specify S3 bucket configuration and file storage strategy

**FR Coverage:** FR11 (Drag-drop), FR12 (Browse files), FR13 (Validate PDF), FR14 (Accept up to 100MB), FR15 (Reject >100MB), FR16 (Upload progress), FR18 (Large file warning)

---

### Story 2.2: PDF Text Extraction with Layout Detection

**As a** system,  
**I want** to extract text blocks with precise layout coordinates from uploaded PDFs,  
**So that** translations can be placed back in the correct positions.

**Acceptance Criteria:**

**Given** an uploaded PDF file  
**When** text extraction is triggered  
**Then** the system extracts all text blocks with:
- Text content
- Page number
- X, Y coordinates (normalized to percentages: 0-100%)
- Font name and size
- Bold/italic styling information
- Block type (paragraph, heading, table cell, caption, etc.)

**And** the extraction completes within 5-10 seconds for a 100-page document  
**And** extracted data is stored in Redis cache with job_id as key  
**And** block-level mapping is created for later reconstruction

**Given** a scanned PDF (no selectable text)  
**When** text extraction is attempted  
**Then** the system detects it is scanned  
**And** OCR processing is triggered (LlamaParse or similar)  
**And** user is notified: "This appears to be a scanned PDF. Processing may take longer for OCR."  
**And** OCR results are stored in the same format as digital PDF extraction

**Given** extraction fails (corrupted PDF, unsupported format)  
**When** the error occurs  
**Then** job status is set to "failed"  
**And** user sees error: "This PDF appears to be corrupted. Please check and try another file."  
**And** error is logged for debugging

**Prerequisites:** Story 2.1 (PDF File Upload)

**Technical Notes:**
- Use PDFMathTranslate library (per sprint-change-proposal-2025-12-13.md) for extraction
- Alternative: PyMuPDF (fitz) for text + layout extraction
- Extract blocks with `page.get_text("dict")` to get block-level information
- Normalize coordinates to percentages for responsive rendering
- Store extraction results in Redis with 24-hour TTL
- OCR fallback: LlamaParse API for scanned PDFs
- Architecture workflow will specify PDFMathTranslate integration details

**FR Coverage:** FR17 (Auto-detect scanned PDF), FR93 (Corrupted PDF error), FR94 (Scanned PDF notification), FR95 (OCR failure handling)

---

### Story 2.3: Language Selection & Source Detection

**As a** user,  
**I want** to select my target language and have the system detect the source language,  
**So that** translation can proceed with the correct language pair.

**Acceptance Criteria:**

**Given** a user has uploaded a PDF  
**When** they view the language selection interface  
**Then** they see a dropdown with target languages: Japanese, Vietnamese  
**And** source language is auto-detected and displayed: "English → [Selected Target]"  
**And** the language pair is clearly displayed: "English → Japanese"

**Given** the system detects source language  
**When** source is not English  
**Then** a warning is displayed: "Source language appears to be [detected language]. MVP only supports English as source. Translation may not work correctly."  
**And** user can override detection by manually selecting source language (if needed)

**Given** a user selects a language pair  
**When** they confirm the selection  
**Then** the language pair is validated (must be supported: English → Japanese or English → Vietnamese)  
**And** if invalid, error: "This language pair is not supported in MVP."  
**And** if valid, translation process begins

**Given** language selection is made  
**When** the selection is stored  
**Then** it is saved in user session for future reference  
**And** supported language pairs are clearly displayed in UI throughout the flow

**Prerequisites:** Story 2.1 (PDF File Upload)

**Technical Notes:**
- Frontend: Language selector component with dropdown
- Source detection: Use language detection library (langdetect or similar) on extracted text sample
- Store language pair in translation_job record
- Display language pair consistently: "English → Japanese" format
- Architecture workflow will specify language detection algorithm

**FR Coverage:** FR21 (Target language dropdown), FR22 (Auto-detect source), FR23 (Non-English warning), FR24 (Override detection), FR25 (Display language pair), FR26 (Validate pair), FR27 (Store in session), FR28 (Display supported pairs)

---

### Story 2.4: DeepL Translation Integration with Batching

**As a** system,  
**I want** to translate extracted text blocks using DeepL API with efficient batching,  
**So that** translations are high-quality and cost-effective.

**Acceptance Criteria:**

**Given** extracted text blocks and selected language pair  
**When** translation is triggered  
**Then** text blocks are batched (10 blocks per API request)  
**And** pages are processed in parallel (multiple pages translated simultaneously)  
**And** DeepL API is called with proper authentication  
**And** translated text is returned for each block

**Given** translation is in progress  
**When** API calls are made  
**Then** progress is tracked per page  
**And** overall progress percentage is calculated  
**And** progress updates are sent to frontend every 2 seconds

**Given** translation completes successfully  
**When** all blocks are translated  
**Then** translated text is stored in Redis cache with job_id  
**And** job status is updated to "translated"  
**And** total translation time is logged

**Given** translation fails (API error, timeout, rate limit)  
**When** error occurs  
**Then** retry logic is applied (3 attempts with exponential backoff)  
**And** if all retries fail, job status is set to "failed"  
**And** user sees error: "Translation failed. Please try again."  
**And** error details are logged for debugging

**Prerequisites:** Story 2.2 (PDF Text Extraction), Story 2.3 (Language Selection)

**Technical Notes:**
- Use DeepL Python client library
- Batch 10 text blocks per API request to optimize cost
- Parallel processing: Process multiple pages simultaneously (use asyncio or Celery)
- Progress tracking: Update job status in database with page count and completion percentage
- Error handling: Retry with exponential backoff (1s, 2s, 4s delays)
- Cost monitoring: Log API usage for cost tracking
- Architecture workflow will specify DeepL API integration and rate limiting

**FR Coverage:** FR31 (Begin translation), FR35 (Complete within 90 seconds), FR36 (Translation failure handling), FR91 (API failure error message)

---

### Story 2.5: Asynchronous Job Processing with Celery

**As a** system,  
**I want** to process translations asynchronously using a job queue,  
**So that** large documents don't block the UI and multiple users can be served simultaneously.

**Acceptance Criteria:**

**Given** a user uploads a PDF and selects language  
**When** translation job is created  
**Then** job is queued in Celery with Redis broker  
**And** job_id is returned to frontend immediately  
**And** frontend can poll for status without blocking

**Given** a translation job is queued  
**When** Celery worker picks up the job  
**Then** job executes: extract → translate → (future: reconstruct)  
**And** job status is updated in database: "queued" → "processing" → "completed"/"failed"  
**And** progress updates are written to Redis for real-time polling

**Given** multiple users upload documents simultaneously  
**When** jobs are queued  
**Then** jobs are processed sequentially per user (one at a time)  
**And** users can see their job in queue position  
**And** system supports 100+ concurrent job queues without degradation

**Given** a user leaves during processing  
**When** 30 minutes pass  
**Then** session is preserved  
**And** user can return and see job status  
**And** completed translations are available for 30 minutes after completion

**Prerequisites:** Story 2.4 (DeepL Translation Integration)

**Technical Notes:**
- Set up Celery with Redis broker
- Create Celery task: `extract_and_translate(job_id, file_path, language_pair)`
- Job status tracking in database: queued, processing, completed, failed
- Progress updates: Store in Redis with job_id key, TTL 1 hour
- Frontend polling: Poll `/api/v1/status/{job_id}` every 2 seconds
- Session preservation: Store job_id in session, allow resume
- Architecture workflow will specify Celery configuration and scaling strategy

**FR Coverage:** FR34 (Async processing), FR37 (Temporary storage in session), FR39 (Session preservation), FR40 (Estimated time remaining)

---

### Story 2.6: Translation Status Polling & Progress Display

**As a** user,  
**I want** to see real-time progress of my translation,  
**So that** I know how long to wait and can see the system is working.

**Acceptance Criteria:**

**Given** a translation job is in progress  
**When** user views the processing page  
**Then** they see a progress indicator with:
- Overall percentage complete (e.g., "45%")
- Current status: "Processing...", "Extracting text...", "Translating page 23 of 100..."
- Estimated time remaining (calculated from processing rate)
- Visual progress bar

**Given** a multi-page document  
**When** translation is processing  
**Then** page-by-page progress is shown: "Page 23 of 100 completed"  
**And** progress updates every 2 seconds via polling

**Given** translation completes  
**When** status changes to "completed"  
**Then** user is automatically redirected to review page  
**And** success message is displayed

**Given** translation fails  
**When** status changes to "failed"  
**Then** error message is displayed: "Translation failed. Please try again."  
**And** retry button is available  
**And** retry reloads original file (doesn't require re-upload)

**Prerequisites:** Story 2.5 (Asynchronous Job Processing)

**Technical Notes:**
- Frontend: TanStack Query with `refetchInterval: 2000` for polling
- Backend: `GET /api/v1/status/{job_id}` endpoint returns: status, progress_percent, current_page, total_pages, estimated_seconds_remaining
- Progress calculation: Based on pages completed / total pages
- ETA calculation: Average time per page * remaining pages
- Auto-redirect: When status = "completed", navigate to review page
- Architecture workflow will specify polling strategy and performance optimization

**FR Coverage:** FR32 (Progress indicator), FR33 (Page-by-page progress), FR36 (Failure error and retry), FR40 (Estimated time remaining), FR92 (Retry from failure point)

---

### Story 2.7: File Cleanup & Session Management

**As a** system,  
**I want** to automatically clean up processed files and manage session expiration,  
**So that** storage costs are controlled and sessions are properly managed.

**Acceptance Criteria:**

**Given** a translation job is completed  
**When** 24 hours pass from job creation  
**Then** temporary files in S3 are automatically deleted  
**And** cached translation data in Redis is expired  
**And** job record in database is marked as "expired" (not deleted, for audit)

**Given** a user session is active  
**When** user is inactive for 12 hours  
**Then** session expires  
**And** user must re-authenticate  
**And** if translation was in progress, job continues but user must sign in to access results

**Given** a cleanup job runs  
**When** files are deleted  
**Then** deletion is logged  
**And** no errors occur if files are already deleted  
**And** cleanup job runs daily via scheduled task (AWS Lambda or Celery beat)

**Prerequisites:** Story 2.5 (Asynchronous Job Processing)

**Technical Notes:**
- Scheduled cleanup: AWS Lambda with EventBridge (daily at 2 AM) or Celery beat
- Cleanup script: Query jobs older than 24 hours, delete S3 files, expire Redis keys
- Session expiration: JWT token expiration set to 12 hours, refresh token mechanism
- Audit trail: Keep job records in database (mark as expired, don't delete)
- Architecture workflow will specify cleanup scheduling and monitoring

**FR Coverage:** FR38 (Auto-delete after 24 hours), FR82 (Session persists 12 hours), FR83 (Session expiration handling), FR87 (No retained copies after download)

---

## Epic 3: Review & Refinement Experience

**Goal:** Provide users with a premium side-by-side review interface, tone customization capabilities, and editing tools to refine translations before downloading. This epic delivers TransKeep's key differentiators: synchronized highlighting, tone-aware translation, and interactive refinement.

**Value:** This is what makes TransKeep special - the review experience is the product. Users can verify accuracy, customize tone, and refine translations until perfect. This epic delivers the core value proposition beyond basic translation.

**FR Coverage:** FR41-70 (Review Interface, Tone Customization, Edit & Alternatives)

---

### Story 3.1: Side-by-Side PDF Review Interface

**As a** user,  
**I want** to see original and translated PDFs side-by-side with synchronized scrolling,  
**So that** I can easily compare and verify translation accuracy.

**Acceptance Criteria:**

**Given** a translation is completed  
**When** user is redirected to review page  
**Then** dual-panel interface is displayed:
- Left panel: Original PDF rendered with pdf.js
- Right panel: Translated PDF rendered with pdf.js
- Both panels show full formatting (images, tables, text styling preserved)
- Panels occupy 90%+ of screen (review is primary focus)

**Given** synchronized scrolling is enabled (default)  
**When** user scrolls in either panel  
**Then** both panels scroll together (synchronized)  
**And** scroll position is maintained across both panels  
**And** scrolling is smooth (60 FPS if possible)

**Given** user wants independent scrolling  
**When** they toggle "Sync Scrolling" off  
**Then** each panel scrolls independently  
**And** toggle state is remembered for session

**Given** user wants to zoom  
**When** they use zoom controls  
**Then** both panels zoom together (maintains sync)  
**And** zoom level is maintained (50% to 200% range)

**Given** user is on mobile/tablet (screen < 768px)  
**When** review page loads  
**Then** side-by-side stacks vertically  
**And** tab toggle allows switching between "Original" and "Translated" views  
**And** touch targets are at least 44x44 pixels

**Prerequisites:** Story 2.6 (Translation Status Polling), Story 2.7 (File Cleanup) - Note: PDF reconstruction needed first, see Story 3.6

**Technical Notes:**
- Frontend: pdf.js for PDF rendering in both panels
- React component: `ReviewPanel` with two `PDFViewer` components
- Synchronized scrolling: Use scroll event listeners, update both panels simultaneously
- Zoom: Use pdf.js zoom API, apply to both viewers
- Responsive: Use CSS media queries, stack on mobile
- State management: Zustand store for scroll sync state, zoom level
- Architecture workflow will specify PDF rendering performance optimization

**FR Coverage:** FR41 (Dual-panel interface), FR42 (Formatting preserved), FR43 (Independent or sync scrolling), FR44 (Default synchronized), FR45 (Toggle sync), FR49 (Zoom in/out), FR50 (Mobile responsive)

---

### Story 3.2: Synchronized Block-Level Highlighting

**As a** user,  
**I want** to hover over text blocks in either PDF to see corresponding sections highlighted in both,  
**So that** I can instantly verify which parts correspond between original and translation.

**Acceptance Criteria:**

**Given** user is viewing side-by-side PDFs  
**When** they hover over any text block in the original PDF  
**Then** that block highlights with color accent (not intrusive, maintains readability)  
**And** corresponding block in translated PDF highlights simultaneously  
**And** highlighting is block-level: paragraphs, table cells, captions, headers

**Given** user hovers over a block in translated PDF  
**When** hover occurs  
**Then** that block highlights  
**And** corresponding block in original PDF highlights  
**And** highlighting works in both directions

**Given** highlighting is active  
**When** user moves mouse away  
**Then** highlighting is removed from both panels  
**And** no visual artifacts remain

**Given** block mapping exists  
**When** user hovers  
**Then** highlighting appears within 100ms (responsive)  
**And** highlight color is accessible (4.5:1 contrast ratio)  
**And** highlight doesn't obscure text readability

**Prerequisites:** Story 3.1 (Side-by-Side Review Interface)

**Technical Notes:**
- Block mapping: Use extracted block coordinates from Story 2.2
- Create mapping: original_block_id → translated_block_id (same semantic content)
- Highlighting: Overlay colored rectangle on PDF canvas using pdf.js annotation layer
- Event handling: Mouse enter/leave events on text blocks
- Performance: Debounce hover events, cache block mappings
- Color: Use CSS variable for highlight color (accessible, configurable)
- Architecture workflow will specify block mapping algorithm and performance optimization

**FR Coverage:** FR46 (Hover highlighting), FR47 (Block-level highlighting), FR48 (Color accent, readable)

---

### Story 3.3: Tone Preset Selection & Application

**As a** user,  
**I want** to select from predefined tone presets to change translation style,  
**So that** I can get translations that match my document's purpose (formal, creative, etc.).

**Acceptance Criteria:**

**Given** user is on review page  
**When** they access "Tone" panel/modal  
**Then** they see 5 predefined tone presets displayed:
- Formal (professional, precise language)
- Casual (conversational, approachable)
- Technical (specialized terminology, accuracy)
- Creative (literary, expressive, nuanced)
- Academic (scholarly, analytical)

**Given** user clicks a tone preset  
**When** preset is selected  
**Then** tone re-translation is triggered  
**And** progress indicator shows: "Applying [Tone] tone... (15-30 seconds)"  
**And** Claude Haiku API is called with translation + tone description

**Given** tone re-translation completes  
**When** new translation is ready  
**Then** translated PDF panel updates with new translation  
**And** user can see new translation immediately in same dual-panel view  
**And** original translation is cached for comparison

**Given** user wants to compare tones  
**When** they switch between tone presets  
**Then** they can see before/after comparison  
**And** tone changes apply within 15-30 seconds  
**And** no limits on tone switching (can switch multiple times)

**Prerequisites:** Story 3.1 (Side-by-Side Review Interface)

**Technical Notes:**
- Frontend: ToneSelector component with 5 preset buttons
- Backend: `POST /api/v1/tone/apply` endpoint
- Claude Haiku integration: Send original text + tone description, get re-translated text
- Caching: Store tone variations in Redis with key: `{job_id}:tone:{tone_name}`
- If same tone applied twice, return cached version (no re-translation)
- Progress: Show loading state during re-translation
- Architecture workflow will specify Claude API integration and caching strategy

**FR Coverage:** FR51 (Access tone panel), FR52 (5 tone presets), FR53 (Click preset), FR54 (Re-translate with tone), FR55 (See new translation), FR56 (Compare tones), FR59 (Switch multiple times), FR60 (Cache tone variations)

---

### Story 3.4: Custom Tone Input & Application

**As a** user,  
**I want** to enter a custom tone description for specialized translation needs,  
**So that** I can get translations that match my specific style requirements.

**Acceptance Criteria:**

**Given** user is in tone panel  
**When** they see custom tone input field  
**Then** field is clearly labeled: "Custom Tone (e.g., 'poetic and romantic', 'funny and casual')"  
**And** placeholder text provides examples  
**And** field accepts free-text input (up to 200 characters)

**Given** user enters custom tone description  
**When** they submit (Enter key or "Apply" button)  
**Then** custom tone is validated (not empty, reasonable length)  
**And** Claude Haiku is called with translation + custom tone description  
**And** re-translation proceeds (15-30 seconds)

**Given** custom tone re-translation completes  
**When** new translation is ready  
**Then** translated PDF panel updates  
**And** custom tone description is stored in session for reuse  
**And** user can see result immediately

**Given** user applies same custom tone twice  
**When** tone matches previous input (exact or similar)  
**Then** cached version is returned (no re-translation)  
**And** response is instant

**Prerequisites:** Story 3.3 (Tone Preset Selection)

**Technical Notes:**
- Frontend: Text input field in ToneSelector component
- Validation: Check for empty, reasonable length (10-200 chars), basic sanity check
- Claude API: Send custom tone description in prompt: "Translate with this tone: [description]"
- Caching: Use fuzzy matching to detect similar custom tones (avoid duplicate API calls)
- Store custom tone in session state for user reference
- Architecture workflow will specify custom tone processing and validation

**FR Coverage:** FR57 (Custom tone input), FR58 (Apply custom tone via Claude)

---

### Story 3.5: Edit Translation Blocks with Alternatives

**As a** user,  
**I want** to click any translated block to edit it and see alternative phrasings,  
**So that** I can refine translations to perfection.

**Acceptance Criteria:**

**Given** user is viewing translated PDF  
**When** they click any text block  
**Then** edit panel appears with:
- Current translation text pre-filled in editable field
- 2-3 alternative phrasings displayed below (generated by Claude)
- "Apply" button to save changes
- "Cancel" button to close panel

**Given** user sees alternatives  
**When** they click an alternative  
**Then** that alternative replaces current translation in edit field  
**And** user can further edit if needed

**Given** user modifies translation (typed edit or selected alternative)  
**When** they click "Apply"  
**Then** edit is saved to session state  
**And** translated PDF view updates immediately with new text  
**And** edit panel closes  
**And** change is tracked for undo functionality

**Given** user wants to undo an edit  
**When** they click "Undo" button or use browser back  
**Then** previous translation is restored  
**And** PDF view updates  
**And** undo history is maintained (up to 10 undos)

**Prerequisites:** Story 3.2 (Synchronized Highlighting)

**Technical Notes:**
- Frontend: EditPanel component that appears on block click
- Block click detection: Use pdf.js text layer click events, map to block coordinates
- Alternatives generation: Call Claude API with block text, request 2-3 alternatives
- Edit tracking: Store edits in Zustand store with block_id → edited_text mapping
- Undo: Maintain edit history stack, pop on undo
- Real-time preview: Update PDF viewer with edited text overlay
- Architecture workflow will specify edit state management and alternatives generation

**FR Coverage:** FR61 (Click to edit), FR62 (Edit panel with pre-filled text), FR63 (Type to modify), FR64 (See alternatives), FR65 (Click alternative), FR66 (Apply edit), FR70 (Undo edits)

---

### Story 3.6: Re-translate Sections with Custom Tone

**As a** user,  
**I want** to re-translate specific sections with a custom tone,  
**So that** I can fine-tune individual parts without re-translating the entire document.

**Acceptance Criteria:**

**Given** user has a block selected for editing  
**When** they see "Re-translate with tone" option  
**Then** they can enter a tone description (e.g., "more formal", "poetic")  
**And** they can click "Re-translate"

**Given** user requests re-translation with tone  
**When** re-translation is triggered  
**Then** Claude Haiku is called with: original source text + tone description  
**And** new translation is generated (5-10 seconds for single block)  
**And** new translation replaces current block text  
**And** edit panel updates with new text

**Given** re-translation completes  
**When** new translation is ready  
**Then** user sees result immediately  
**And** can accept, edit further, or request different tone  
**And** change is tracked in edit history

**Prerequisites:** Story 3.5 (Edit Translation Blocks)

**Technical Notes:**
- Frontend: Add "Re-translate" button in EditPanel
- Backend: `POST /api/v1/retranslate` endpoint with block_id, tone_description
- Claude API: Send original source text (from extraction) + tone, get new translation
- Store original source text mapping: block_id → source_text (needed for re-translation)
- Update edit state with new translation
- Architecture workflow will specify re-translation API design

**FR Coverage:** FR67 (Re-translate with custom tone), FR68 (Apply tone-specific re-translation)

---

### Story 3.7: PDF Reconstruction with Translated Text

**As a** system,  
**I want** to reconstruct PDFs with translated text in original positions,  
**So that** users see formatted translated documents ready for download.

**Acceptance Criteria:**

**Given** translation is completed and user views review page  
**When** PDF reconstruction is needed  
**Then** system uses PDFMathTranslate library to reconstruct PDF  
**And** translated text is placed in original block positions  
**And** original formatting is preserved: fonts, spacing, images, layout  
**And** text expansion/contraction is handled (font size adjustment if needed)

**Given** user makes edits or applies tone changes  
**When** PDF needs to be updated  
**Then** reconstruction is triggered with latest edits/tone  
**And** new PDF is generated  
**And** translated panel updates with new PDF

**Given** reconstruction completes  
**When** PDF is ready  
**Then** it is stored temporarily in S3  
**And** pre-signed URL is generated for frontend access  
**And** PDF is available for download

**Prerequisites:** Story 2.2 (PDF Text Extraction), Story 2.4 (DeepL Translation), Story 3.5 (Edit Blocks)

**Technical Notes:**
- Use PDFMathTranslate library (per sprint-change-proposal-2025-12-13.md) for reconstruction
- Alternative: PyMuPDF for text insertion with original coordinates
- Handle text expansion: Adjust font size if translated text is longer than original
- Preserve images, tables, and layout elements from original PDF
- Store reconstructed PDF in S3 with job_id
- Generate pre-signed URL for frontend PDF viewer access
- Architecture workflow will specify PDFMathTranslate integration and reconstruction algorithm

**FR Coverage:** FR42 (Formatting preserved - enables review), FR72 (Generate final PDF with edits), FR73 (Preserve formatting)

---

## Epic 4: Download & System Management

**Goal:** Enable users to download final translated PDFs, manage sessions, handle errors gracefully, and maintain system operations. This epic completes the user journey and ensures system reliability.

**Value:** Without download, users cannot get their translated documents. Without proper error handling and session management, the system is unreliable. This epic delivers completion and reliability.

**FR Coverage:** FR71-100 (Download, Session Management, Error Handling)

---

### Story 4.1: Download Translated PDF with Edits Applied

**As a** user,  
**I want** to download my final translated PDF with all edits and tone customizations,  
**So that** I have the polished document ready for use.

**Acceptance Criteria:**

**Given** user has reviewed and edited translation  
**When** they click "Download Translated PDF"  
**Then** system generates final PDF with:
- All edits applied (from edit history)
- All tone customizations applied
- Original formatting preserved
- TransKeep branding/watermark (optional, may remove for paid tier)

**Given** final PDF is generated  
**When** download is triggered  
**Then** download progress is displayed (usually instant for small files, 5-10 sec for large)  
**And** file downloads with name: "{original_filename}_translated_{target_language}.pdf"  
**And** download completes successfully

**Given** download completes  
**When** file is saved  
**Then** user sees confirmation: "Download complete: [filename]"  
**And** user can download same translation multiple times without re-processing

**Given** user downloads translation  
**When** download is requested again  
**Then** cached PDF is returned (no re-processing)  
**And** download is instant

**Prerequisites:** Story 3.7 (PDF Reconstruction)

**Technical Notes:**
- Backend: `GET /api/v1/download/{job_id}` endpoint
- Apply all edits from session state to final PDF
- Apply tone customizations (use cached tone variation)
- Generate PDF with PDFMathTranslate or PyMuPDF
- Add watermark if configured (check subscription tier)
- Generate pre-signed S3 URL for download
- Frontend: Trigger browser download via blob URL or direct link
- Cache final PDF in S3 for 24 hours (allow re-download)
- Architecture workflow will specify download optimization and caching

**FR Coverage:** FR71 (Download button), FR72 (Generate final PDF), FR73 (Preserve formatting), FR74 (Download progress), FR75 (Filename format), FR76 (Multiple downloads), FR77 (Download confirmation), FR80 (Branding/watermark)

---

### Story 4.2: Session State Management & Persistence

**As a** user,  
**I want** my work (edits, tone changes) to persist during my session,  
**So that** I don't lose progress if I navigate away temporarily.

**Acceptance Criteria:**

**Given** user makes edits or applies tone changes  
**When** changes are made  
**Then** all work is stored in session state (Zustand store + backend session)  
**And** session persists for 12 hours of inactivity  
**And** user can navigate away and return without losing work

**Given** user session is active  
**When** 12 hours of inactivity pass  
**Then** session expires  
**And** user must re-authenticate  
**And** if translation was in progress, job continues but user must sign in to access

**Given** user closes browser  
**When** browser is closed  
**Then** warning is shown before closing (if unsaved work exists): "You have unsaved changes. Are you sure you want to leave?"  
**And** if user confirms, work is lost (MVP: no auto-save to database)  
**And** if user cancels, browser stays open

**Given** user returns after session expiration  
**When** they sign in again  
**Then** they must re-upload document (MVP: no project history)  
**And** previous work is not available

**Prerequisites:** Story 3.5 (Edit Blocks), Story 3.3 (Tone Selection)

**Technical Notes:**
- Frontend: Zustand store for session state (edits, tone selections)
- Backend: Store session data in Redis with user_id + session_id key
- Session expiration: 12-hour TTL in Redis, JWT token expiration
- Browser warning: Use `beforeunload` event to warn on unsaved changes
- MVP limitation: No persistent project storage (Phase 2 feature)
- Architecture workflow will specify session management strategy

**FR Coverage:** FR81 (Session-based work), FR82 (12-hour persistence), FR83 (Session expiration), FR84 (Browser close warning), FR85 (No project history in MVP), FR86 (Independent translations)

---

### Story 4.3: Comprehensive Error Handling & User Messages

**As a** user,  
**I want** clear, helpful error messages when things go wrong,  
**So that** I understand what happened and what to do next.

**Acceptance Criteria:**

**Given** translation API fails  
**When** error occurs  
**Then** user sees: "Translation failed. Please try again."  
**And** retry button is available  
**And** error includes support contact or help link  
**And** error is logged for debugging

**Given** PDF is corrupted or invalid  
**When** validation fails  
**Then** user sees: "This PDF appears to be corrupted. Please check and try another file."  
**And** upload is rejected  
**And** user can try a different file

**Given** scanned PDF OCR fails  
**When** OCR processing fails  
**Then** user sees: "Could not extract text from this scanned PDF. Please ensure image quality is good."  
**And** user can try a different file or improve image quality

**Given** any operation exceeds expected time by 30%  
**When** timeout occurs  
**Then** user sees timeout message: "This is taking longer than expected. Please wait or try again."  
**And** operation continues in background  
**And** user can check status

**Given** user's internet disconnects  
**When** connection is lost during upload/translation  
**Then** system stores state  
**And** allows resume on reconnection  
**And** user sees: "Connection lost. Reconnecting..." message

**Given** free tier user reaches limit mid-translation  
**When** limit is reached  
**Then** current translation completes  
**And** upgrade prompt is shown for next translation  
**And** current work is not blocked

**Prerequisites:** Story 2.4 (DeepL Translation), Story 2.1 (File Upload), Story 1.4 (Subscription Management)

**Technical Notes:**
- Error handling: Try-catch blocks around all API calls, database operations
- User-friendly messages: Map technical errors to user-friendly text
- Support links: Include help/support URL in all error messages
- Logging: Log all errors with context (user_id, job_id, error details) for debugging
- Retry logic: Provide retry buttons for transient errors
- Network handling: Detect connection loss, store state, allow resume
- Architecture workflow will specify error handling strategy and monitoring

**FR Coverage:** FR91 (Translation API failure), FR92 (Retry from failure), FR93 (Corrupted PDF), FR94 (Scanned PDF notification), FR95 (OCR failure), FR96 (Internet disconnect), FR97 (Free tier limit), FR98 (Support links), FR99 (Error logging), FR100 (Timeout messages)

---

### Story 4.4: System Metrics & Analytics Logging

**As a** system administrator,  
**I want** basic metrics logged for analytics and monitoring,  
**So that** I can track usage and identify issues.

**Acceptance Criteria:**

**Given** any user action occurs  
**When** action is performed  
**Then** relevant metrics are logged:
- Upload count per user
- Successful translations count
- Failed translations count
- Error types and frequencies
- Processing times
- User subscription tiers

**Given** metrics are logged  
**When** logs are written  
**Then** logs include: timestamp, user_id (anonymized if needed), action type, result  
**And** no sensitive data (document content) appears in logs  
**And** logs are stored for 30 days minimum

**Given** analytics are needed  
**When** metrics are queried  
**Then** aggregated statistics are available:
- Total documents translated
- Average processing time
- Error rate
- User engagement metrics

**Prerequisites:** Story 1.3 (Google OAuth), Story 2.1 (File Upload)

**Technical Notes:**
- Logging: Use structured logging (JSON format) with OpenTelemetry
- Metrics: Track in database (analytics table) or time-series database
- Anonymization: Hash user_id for analytics, keep full user_id for operational logs
- No PII: Never log document content, only metadata
- Retention: 30-day retention for operational logs, longer for analytics
- Architecture workflow will specify logging infrastructure and analytics platform

**FR Coverage:** FR89 (Log basic metrics)

---

### Story 4.5: Account Deletion & Data Cleanup

**As a** user,  
**I want** to delete my account and all associated data,  
**So that** I have control over my privacy.

**Acceptance Criteria:**

**Given** a user wants to delete their account  
**When** they access account settings  
**Then** they see "Delete Account" option  
**And** confirmation dialog warns: "This will permanently delete your account and all data. This cannot be undone."

**Given** user confirms account deletion  
**When** deletion is processed  
**Then** all user data is deleted:
- User record in database
- All translation jobs and associated files in S3
- All session data in Redis
- Subscription records (if applicable)
- Analytics data (anonymized or deleted per privacy policy)

**Given** account is deleted  
**When** deletion completes  
**Then** user receives confirmation email  
**And** user is signed out  
**And** user cannot access account anymore

**Prerequisites:** Story 1.3 (Google OAuth), Story 2.1 (File Upload)

**Technical Notes:**
- Backend: `DELETE /api/v1/user/account` endpoint
- Cascade deletion: Delete all related records (jobs, subscriptions, sessions)
- S3 cleanup: Delete all user files from S3
- Redis cleanup: Delete all user session keys
- Confirmation email: Send before deletion (optional: delay 7 days for recovery)
- Audit trail: Log account deletion for compliance (keep minimal record)
- Architecture workflow will specify data deletion strategy and compliance requirements

**FR Coverage:** FR90 (Delete account)

---

## FR Coverage Matrix

This matrix maps each Functional Requirement (FR) to the Epic and Story that implements it.

### Epic 1: Foundation & User Authentication

| FR | Description | Story |
|---|---|---|
| FR1 | Google OAuth sign-in | Story 1.3 |
| FR2 | Persistent authentication | Story 1.3 |
| FR3 | Log out | Story 1.3 |
| FR4 | Track subscription tier | Story 1.2, Story 1.4 |
| FR5 | Free tier counter | Story 1.4 |
| FR6 | Upgrade prompt | Story 1.4 |
| FR7 | Paid unlimited | Story 1.4 |
| FR8 | Subscription status display | Story 1.4 |
| FR9 | Cancel subscription | Story 1.5 |
| FR10 | Email confirmation | Story 1.5 |

### Epic 2: Document Upload & Translation Pipeline

| FR | Description | Story |
|---|---|---|
| FR11 | Drag-drop PDF | Story 2.1 |
| FR12 | Browse and select PDF | Story 2.1 |
| FR13 | Validate PDF file | Story 2.1 |
| FR14 | Accept up to 100MB | Story 2.1 |
| FR15 | Reject >100MB | Story 2.1 |
| FR16 | Upload progress | Story 2.1 |
| FR17 | Auto-detect scanned PDF | Story 2.2 |
| FR18 | Large file warning | Story 2.1 |
| FR19 | Simultaneous uploads | Story 2.1 |
| FR20 | Queue sequential processing | Story 2.5 |
| FR21 | Target language dropdown | Story 2.3 |
| FR22 | Auto-detect source language | Story 2.3 |
| FR23 | Non-English warning | Story 2.3 |
| FR24 | Override source detection | Story 2.3 |
| FR25 | Display language pair | Story 2.3 |
| FR26 | Validate language pair | Story 2.3 |
| FR27 | Store language in session | Story 2.3 |
| FR28 | Display supported pairs | Story 2.3 |
| FR31 | Begin translation | Story 2.4 |
| FR32 | Progress indicator | Story 2.6 |
| FR33 | Page-by-page progress | Story 2.6 |
| FR34 | Async processing | Story 2.5 |
| FR35 | Complete within 90 seconds | Story 2.4 |
| FR36 | Translation failure handling | Story 2.4, Story 2.6 |
| FR37 | Temporary storage in session | Story 2.5 |
| FR38 | Auto-delete after 24 hours | Story 2.7 |
| FR39 | Session preservation | Story 2.5 |
| FR40 | Estimated time remaining | Story 2.6 |

### Epic 3: Review & Refinement Experience

| FR | Description | Story |
|---|---|---|
| FR41 | Dual-panel interface | Story 3.1 |
| FR42 | Formatting preserved | Story 3.1, Story 3.7 |
| FR43 | Independent or sync scrolling | Story 3.1 |
| FR44 | Default synchronized | Story 3.1 |
| FR45 | Toggle sync scrolling | Story 3.1 |
| FR46 | Hover highlighting | Story 3.2 |
| FR47 | Block-level highlighting | Story 3.2 |
| FR48 | Color accent highlighting | Story 3.2 |
| FR49 | Zoom in/out | Story 3.1 |
| FR50 | Mobile responsive | Story 3.1 |
| FR51 | Access tone panel | Story 3.3 |
| FR52 | 5 tone presets | Story 3.3 |
| FR53 | Click preset | Story 3.3 |
| FR54 | Re-translate with tone | Story 3.3 |
| FR55 | See new translation | Story 3.3 |
| FR56 | Compare tones | Story 3.3 |
| FR57 | Custom tone input | Story 3.4 |
| FR58 | Apply custom tone | Story 3.4 |
| FR59 | Switch tones multiple times | Story 3.3 |
| FR60 | Cache tone variations | Story 3.3 |
| FR61 | Click to edit | Story 3.5 |
| FR62 | Edit panel with pre-filled | Story 3.5 |
| FR63 | Type to modify | Story 3.5 |
| FR64 | See alternatives | Story 3.5 |
| FR65 | Click alternative | Story 3.5 |
| FR66 | Apply edit | Story 3.5 |
| FR67 | Re-translate with tone | Story 3.6 |
| FR68 | Apply tone re-translation | Story 3.6 |
| FR69 | Track edits in session | Story 3.5, Story 4.2 |
| FR70 | Undo edits | Story 3.5 |

### Epic 4: Download & System Management

| FR | Description | Story |
|---|---|---|
| FR71 | Download button | Story 4.1 |
| FR72 | Generate final PDF | Story 4.1 |
| FR73 | Preserve formatting | Story 4.1 |
| FR74 | Download progress | Story 4.1 |
| FR75 | Filename format | Story 4.1 |
| FR76 | Multiple downloads | Story 4.1 |
| FR77 | Download confirmation | Story 4.1 |
| FR78 | Bilingual PDF (Phase 2) | Deferred |
| FR79 | Export formats (Phase 2) | Deferred |
| FR80 | Branding/watermark | Story 4.1 |
| FR81 | Session-based work | Story 4.2 |
| FR82 | 12-hour persistence | Story 4.2 |
| FR83 | Session expiration | Story 4.2 |
| FR84 | Browser close warning | Story 4.2 |
| FR85 | No project history (MVP) | Story 4.2 |
| FR86 | Independent translations | Story 4.2 |
| FR87 | No retained copies | Story 2.7 |
| FR88 | Multi-tenant isolation | Story 1.2 |
| FR89 | Log metrics | Story 4.4 |
| FR90 | Delete account | Story 4.5 |
| FR91 | Translation API failure | Story 4.3 |
| FR92 | Retry from failure | Story 2.6, Story 4.3 |
| FR93 | Corrupted PDF error | Story 2.2, Story 4.3 |
| FR94 | Scanned PDF notification | Story 2.2, Story 4.3 |
| FR95 | OCR failure | Story 2.2, Story 4.3 |
| FR96 | Internet disconnect | Story 4.3 |
| FR97 | Free tier limit | Story 4.3 |
| FR98 | Support links in errors | Story 4.3 |
| FR99 | Error logging | Story 4.3 |
| FR100 | Timeout messages | Story 4.3 |

**Total Coverage:** 100/100 FRs (100%)  
**Deferred (Phase 2):** FR78, FR79

---

## Summary

**Epic Breakdown Complete (Initial Version)**

This document provides the complete epic and story breakdown for TransKeep, covering all 100 functional requirements from the PRD. The breakdown is organized into 4 epics with 25 stories total, each sized for single-session completion by a development agent.

**Key Characteristics:**
- ✅ All 100 FRs mapped to stories
- ✅ Epic 1 establishes foundation (infrastructure + authentication)
- ✅ Stories are vertically sliced (deliver complete functionality)
- ✅ No forward dependencies (only backward references)
- ✅ BDD acceptance criteria for all stories
- ✅ Technical notes provide implementation guidance

**Next Steps in BMad Method:**

1. **UX Design** (if UI exists) - Run: `workflow ux-design`
   → Will add interaction details to stories in epics.md

2. **Architecture** - Run: `workflow create-architecture`
   → Will add technical details to stories in epics.md

3. **Phase 4 Implementation** - Stories ready for context assembly

**Important:** This is a living document that will be updated as you progress through the workflow chain. The epics.md file will evolve with UX and Architecture inputs before implementation begins.

---

_For implementation: Use the `create-story` workflow to generate individual story implementation plans from this epic breakdown._

_This document will be updated after UX Design and Architecture workflows to incorporate interaction details and technical decisions._
