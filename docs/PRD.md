# TransKeep - Product Requirements Document

**Author:** Roy  
**Date:** November 14, 2025  
**Version:** 1.0  
**Track:** Enterprise Method - Greenfield  

---

## Executive Summary

**TransKeep** is a premium document translation platform that prioritizes **translation quality**, **user control through review**, and **professional presentation**.

Unlike generic translation tools (Google, DeepL), TransKeep solves a critical gap: **users have no good way to verify translations and no control over tone**. TransKeep fixes this with three integrated capabilities:

1. **Side-by-side review with synchronized highlighting** — Verify accuracy instantly without manual comparison
2. **Tone customization** — Adjust translation tone (Formal, Casual, Creative, etc.) for the right voice
3. **Edit & refine workflow** — See alternatives, edit inline, re-translate sections before downloading

**Market:** Individual users seeking high-quality translations (novels, academic papers, professional documents) where verification and polish matter.

**Platform:** Web-first SaaS with modern, premium UI (Figma aesthetic).

### What Makes TransKeep Special

TransKeep owns three differentiators working together:

- **Review-first UX**: The review experience is the product. Synchronized highlighting makes verification effortless. No other translation tool optimizes for this.
- **Tone-aware translation**: Creative translation for literary works, precise translation for technical docs, formal for business. Users describe the tone they want.
- **Premium design**: Modern, beautiful interface that feels professional and trustworthy. Users feel confident downloading the result.

---

## Project Classification

**Technical Type:** Web SaaS Application (React + FastAPI + Multi-tenant)  
**Domain:** Document Translation & Localization  
**Complexity:** Moderate (standard web SaaS patterns, no regulated domain)  

**Key Architecture Notes:**
- Multi-tenant from Day 1 (supports individuals at launch, enterprises in Phase 2)
- Stateless backend for horizontal scaling
- Async job processing for large PDFs
- OAuth-based user authentication (Google sign-in)

---

## Success Criteria

### MVP Launch Success (Month 1)

**Translation Quality:**
- ✅ Users report translations read better than Google Translate
- Measurement: In-app feedback/ratings after download
- Target: 70%+ of users rate quality as "good" or "excellent"

**Review Experience Adoption:**
- ✅ Users demonstrate passion/engagement with side-by-side review
- Measurement: % of users who use hover-highlighting feature, time spent reviewing
- Target: 60%+ of users actively use review feature (not just download immediately)

**Market Validation:**
- ✅ Achieve 50+ document downloads in first month
- Measurement: Download tracking in analytics
- Target: 50+ paid downloads (post-free-tier-limit users)

**User Satisfaction:**
- ✅ Users would recommend to a friend
- Measurement: NPS score or "would recommend" survey
- Target: NPS 40+

### Long-term Success Indicators

- Return user rate: 40%+ of users translate 2+ documents
- Subscription conversion: 15%+ of users upgrade from free tier
- Enterprise adoption: Phase 2 readiness with collaborative workflows

---

## Product Scope

### MVP - Minimum Viable Product (Launch Day 1)

**What's Included:**

**1. Document Upload & Translation**
- PDF upload (drag-drop, up to 100MB)
- Language pairs: English ↔ Japanese, English ↔ Vietnamese
- Format-preserving translation (original layout maintained)
- Processing time: Complete translation within 90 seconds for 100-page documents

**2. Side-by-Side Review Interface**
- Left panel: Original PDF rendered
- Right panel: Translated PDF rendered
- Synchronized scrolling (both move together)
- Hover-highlighting: Hovering over any block highlights corresponding section in both versions
- Block-level mapping (paragraph, table, image caption level)

**3. Tone Customization**
- Predefined tone presets: Formal, Casual, Technical, Creative, Academic
- Custom tone input: Free-form description (e.g., "poetic and romantic")
- Quick re-apply: Change tone and see result refresh

**4. Edit & Alternatives Workflow**
- Click any translated section to edit inline
- View 2-3 alternative phrasings (different ways to translate the same concept)
- Re-translate specific sections with custom tone
- Real-time preview of changes

**5. Download & Export**
- Download translated PDF with formatting preserved
- Bilingual version option (optional Phase 2)
- One-click download, high-quality output

**6. User Authentication & Freemium Model**
- Google OAuth sign-in (single sign-on)
- Free tier: 2 documents per month
- Upgrade prompt after 2 free documents
- Subscription tier unlocks unlimited documents (pricing TBD)

**7. System Reliability**
- No data loss during translation process
- Automatic cleanup of processed files after 24 hours
- Session-based state (no required user history for MVP)

---

### Growth Features (Post-MVP, Phase 2)

- ✅ Enterprise collaboration: Simultaneous editing, comments, suggestions
- ✅ Glossary management: Terminology databases with auto-apply across documents
- ✅ Additional languages: Expand to 10-15 language pairs based on demand
- ✅ Format expansion: DOCX, PPTX support
- ✅ User history & projects: Save translations, organize by project
- ✅ Bilingual PDF export: Side-by-side original/translated in single file
- ✅ Translation memory: Learn from user's previous translations
- ✅ API access: Programmatic translation for developers
- ✅ Mobile native apps: iOS/Android applications

---

### Vision (Future - Phase 3+)

- Advanced domain models: Specialized models for medical, legal, technical domains
- AI-powered suggestions: System proactively suggests tone adjustments
- Community features: Share translations, get feedback from native speakers
- Custom LLM fine-tuning: Train models on user's terminology and style
- Real-time collaboration: Live co-editing with multiple users
- Integration ecosystem: Slack, Google Docs, Microsoft 365 plugins

---

## Functional Requirements

### FR1-10: User Account & Authentication

**FR1:** Users can create an account via Google OAuth sign-in (no email/password signup)

**FR2:** Users remain logged in across browser sessions (persistent authentication)

**FR3:** Users can log out at any time

**FR4:** System tracks whether user is on free tier or paid subscription

**FR5:** Free tier users see a counter: "X of 2 documents used this month"

**FR6:** When free tier limit reached, user sees upgrade prompt (not a hard block, just messaging)

**FR7:** Paid subscribers have unlimited document uploads and translations

**FR8:** System displays current subscription status and renewal date for paid users

**FR9:** Users can cancel subscription anytime

**FR10:** System sends email confirmation for subscription changes

---

### FR11-20: Document Upload & File Handling

**FR11:** Users can drag-drop PDF files onto upload area

**FR12:** Users can click to browse and select PDF files

**FR13:** System validates file is actually a PDF (not other formats disguised as PDF)

**FR14:** System accepts files up to 100MB in size

**FR15:** System rejects files larger than 100MB with clear error message

**FR16:** System displays upload progress with file size and estimated time

**FR17:** System auto-detects if PDF is digital or scanned (uses OCR for scanned)

**FR18:** System displays warning for very large files (50MB+) with estimated processing time

**FR19:** System supports simultaneous uploads (user can prepare next document while one is processing)

**FR20:** System queues and processes uploads sequentially if multiple attempted simultaneously

---

### FR21-30: Language Selection & Source Detection

**FR21:** Users select target language from dropdown: Japanese, Vietnamese

**FR22:** System auto-detects source language (English detection for MVP)

**FR23:** If source language is not English, system warns user (MVP only supports English source)

**FR24:** Users can override source language detection if needed

**FR25:** System displays language pair clearly: "English → Japanese"

**FR26:** System validates language pair is supported before translation

**FR27:** For future expansion, system stores selected language in user session

**FR28:** System displays supported language pairs clearly in UI

---

### FR31-40: Translation Processing & Status

**FR31:** System begins translation after user selects target language and confirms

**FR32:** System displays progress indicator while translating (% complete or "processing...")

**FR33:** For documents with multiple pages, system shows page-by-page progress

**FR34:** System processes large documents asynchronously (doesn't block UI)

**FR35:** System completes translation within 90 seconds for typical 100-page document

**FR36:** If translation fails (API error, timeout, etc.), system displays user-friendly error and options to retry

**FR37:** System stores temporary translation results in memory/session (not persistent database for MVP)

**FR38:** System auto-deletes processed files 24 hours after creation (cleanup job)

**FR39:** If user leaves during processing, session is preserved for 30 minutes to resume

**FR40:** System displays estimated time remaining during processing

---

### FR41-50: Side-by-Side Review Interface

**FR41:** After translation completes, system displays dual-panel interface: left (original) and right (translated)

**FR42:** Both PDF panels render with full formatting preserved (images, tables, text styling)

**FR43:** Users can scroll within each panel independently or scroll together (sync toggle)

**FR44:** Default: Synchronized scrolling (both panels move together for easy comparison)

**FR45:** Users can toggle synchronized scrolling on/off

**FR46:** When user hovers over any text block in original, corresponding block in translation highlights (and vice versa)

**FR47:** Highlighting is block-level: paragraphs, table cells, captions, headers

**FR48:** Highlighting uses color accent (not intrusive, maintains readability)

**FR49:** Users can zoom in/out on both panels (maintains sync)

**FR50:** Mobile/tablet: Side-by-side stacks vertically on small screens, with tab toggle between original/translated

---

### FR51-60: Tone Customization

**FR51:** After review, users access "Tone" panel/modal

**FR52:** Tone panel displays 5 predefined tone presets:
- Formal (professional, precise language)
- Casual (conversational, approachable)
- Technical (specialized terminology, accuracy)
- Creative (literary, expressive, nuanced)
- Academic (scholarly, analytical)

**FR53:** Users can click any preset to apply it

**FR54:** Applying tone re-translates the document with that style (takes 15-30 seconds)

**FR55:** Users can see new translation immediately after tone applied (same dual-panel view)

**FR56:** Users can compare: original tone vs new tone side-by-side (show before/after)

**FR57:** Users can enter custom tone description: free-text field like "poetic and romantic" or "funny and casual"

**FR58:** System applies custom tone via Claude Haiku (re-translates with that description)

**FR59:** Users can switch between tone options multiple times (no limits)

**FR60:** System caches tone variations to avoid re-translating if user applies same tone twice

---

### FR61-70: Edit & Alternatives Workflow

**FR61:** Users can click any text block in the translated version to edit

**FR62:** Clicking opens an edit panel with that block's translation pre-filled

**FR63:** Users can type in the edit field to modify the translation

**FR64:** Users can see 2-3 alternative phrasings for that block (generated by Claude)

**FR65:** Users can click any alternative to select it (replaces current translation)

**FR66:** Clicking "Apply" saves the edit and updates the translated PDF view

**FR67:** Users can re-translate with a custom tone: "Translate this with [tone description]"

**FR68:** System applies tone-specific re-translation and shows result immediately

**FR69:** Edits are tracked in session (not permanent until download)

**FR70:** Users can undo edits using browser back or explicit "Undo" button

---

### FR71-80: Download & Export

**FR71:** After user finishes reviewing/editing, they click "Download Translated PDF"

**FR72:** System generates final PDF with all edits and tone customizations applied

**FR73:** Final PDF preserves original formatting: fonts, spacing, images, layout

**FR74:** System displays download progress (usually instant for small files, 5-10 sec for large)

**FR75:** Downloaded file is named: "{original_filename}_translated_{target_language}.pdf"

**FR76:** Users can download the same translation multiple times without re-processing

**FR77:** Users receive confirmation when download completes

**FR78:** Optional future: Users can download original + translated as bilingual PDF (Phase 2)

**FR79:** Optional future: Users can export as DOCX or other formats (Phase 2)

**FR80:** System includes TransKeep branding/watermark (optional, may remove for paid tier)

---

### FR81-90: Session & State Management

**FR81:** All user work (edits, tone customizations) is session-based

**FR82:** User session persists for 12 hours of inactivity

**FR83:** After session expires, user must re-upload to continue (for MVP simplicity)

**FR84:** If user closes browser, all unsaved work is lost (warning before closing)

**FR85:** Users cannot save "projects" or history in MVP (Phase 2 feature)

**FR86:** Each translation is independent (no linking between documents)

**FR87:** System does not retain copies of user's documents after download

**FR88:** User data is not shared between users (multi-tenant isolation)

**FR89:** System logs basic metrics (upload count, successful translations, errors) for analytics

**FR90:** User can delete their account anytime (deletes all associated data)

---

### FR91-100: Error Handling & Edge Cases

**FR91:** If translation API fails, system displays: "Translation failed. Please try again."

**FR92:** User can retry translation from failure point (reload original, not re-upload)

**FR93:** If PDF is corrupted/invalid, system displays: "This PDF appears to be corrupted. Please check and try another file."

**FR94:** If PDF is scanned (no selectable text), system notifies user: "This appears to be a scanned PDF. Processing may take longer for OCR."

**FR95:** If OCR fails on scanned PDF, system displays: "Could not extract text from this scanned PDF. Please ensure image quality is good."

**FR96:** If user's internet disconnects during upload/translation, system stores state and allows resume on reconnection

**FR97:** If user runs out of free tier limit mid-translation, system completes current translation and prompts upgrade for next

**FR98:** All error messages include support contact or help link

**FR99:** System logs all errors for monitoring and debugging

**FR100:** System displays timeout messages if any operation exceeds expected time by 30%

---

## Non-Functional Requirements

### Performance Requirements

**Processing Speed:**
- PDF extraction: Complete within 5-10 seconds for 100-page document
- Translation API calls: 30-60 seconds for typical 100-page document (depends on API)
- Tone customization: 15-30 seconds to re-translate with new tone
- **MVP Target Total:** 45-90 seconds from upload to initial translation ready for review

**UI Responsiveness:**
- Page loads in < 2 seconds (first contentful paint)
- All interactions (clicks, hovers, scrolling) respond within 100ms
- Dual-panel scrolling sync is smooth (60 FPS if possible)

**Concurrent Users:**
- System supports 100+ simultaneous document uploads without degradation
- No single-user bottleneck (async processing)

---

### Security Requirements

**Data Protection:**
- All data in transit encrypted (HTTPS/TLS)
- Uploaded PDFs are not permanently stored (deleted after 24 hours)
- No sensitive data logged (user documents never appear in logs)

**User Privacy:**
- Google OAuth tokens handled securely
- No third-party cookies or tracking (except analytics)
- GDPR/Privacy Policy compliant

**Access Control:**
- Users can only access their own translations
- Multi-tenant isolation: No data leakage between users
- Free tier cannot access paid features (enforced server-side)

---

### Scalability Requirements

**Multi-Tenant Architecture:**
- System designed to support unlimited users
- Each user is isolated at data level
- Subscription tiers enforced server-side (not just frontend)

**Horizontal Scaling:**
- Stateless backend (no in-memory session state)
- Can spawn new server instances for load balancing
- Job queue (Celery + Redis) scales independently

**Database:**
- PostgreSQL stores metadata (users, subscription info)
- Does not store document content permanently
- Can scale with read replicas if needed

**Temporary Storage:**
- S3 used for temporary file storage during processing
- Auto-cleanup of old files (24-hour TTL)
- Scales automatically with S3

---

### Accessibility Requirements

**Keyboard Navigation:**
- All interactive elements accessible via keyboard (Tab, Enter, Arrow keys)
- No keyboard traps
- Focus indicator visible at all times

**Screen Reader Support:**
- PDF viewer elements labeled for screen readers (alt text for images)
- Tone panel radio buttons properly labeled
- Error messages announced to screen readers

**Visual Accessibility:**
- Color contrast ratio at least 4.5:1 for text
- UI doesn't rely solely on color (tone preset names also visible)
- Font size 14px minimum for body text

**Mobile Accessibility:**
- Touch targets at least 44x44 pixels
- Readable on all device sizes (responsive design)

---

### Reliability Requirements

**Uptime:**
- Target 99% uptime during business hours (can have maintenance windows)
- System monitors all critical services and alerts on failures

**Data Integrity:**
- No data loss during normal operations
- Session data backed up to handle server crashes
- Graceful degradation if any component fails

**Error Recovery:**
- Failed translations can be retried without data loss
- Temporary S3 files not lost if processing fails
- Jobs can be reprocessed from queue if needed

---

## UX Principles & Design Philosophy

### Core Philosophy: "Premium, Focused, Trustworthy"

TransKeep's design should feel:
- **Premium**: Modern, polished, high-quality (Figma aesthetic, not clunky)
- **Focused**: Every element serves a purpose, minimal clutter
- **Trustworthy**: Users feel confident the translation is good and the interface is reliable

### Key Interaction Patterns

**1. Upload & Preparation**
- Drag-drop as primary interaction (intuitive, low friction)
- Larger drop zone (50%+ of screen)
- Inline language selection without leaving upload screen

**2. Review as Primary Experience**
- Dual panels occupy 90%+ of screen (review dominates)
- Synchronized highlighting is the star feature
- Subtle visual feedback (color highlight, not distracting)

**3. Tone Selection: Preset-First, Custom-Flexible**
- Presets displayed visually (icons or badges, not just text)
- Custom tone input is secondary (not hidden, but optional)
- Tone changes show immediate preview (no "Apply" button, just refresh)

**4. Edit Workflow: Click → Edit → See Result**
- Click any translated block → edit panel appears
- Alternatives shown inline (not modal)
- Changes apply immediately (no confirmation dialog)

**5. Download: Confidence-High, One-Click**
- Download button prominent, clear
- Filename helpful (includes language pair)
- Success message confirms download happened

### Design Specifics

**Color Palette:**
- Modern, premium aesthetic
- Use accent color for highlighting (not jarring, but clear)
- Neutral backgrounds with strategic use of color

**Typography:**
- Clean, modern font (system fonts or premium web fonts)
- Hierarchy clear: headings, body, captions
- Minimum 14px for body text (accessibility)

**Spacing & Layout:**
- Generous whitespace (premium feel)
- Clear visual separation between sections
- Balanced layout that guides the eye

**Interactive Elements:**
- Buttons feel clickable (clear visual states: hover, active, disabled)
- Transitions smooth but fast (not sluggish)
- Feedback immediate (user always knows what happened)

---

## Technical Architecture Overview

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- shadcn/ui components (modern, premium aesthetic)
- Tailwind CSS for styling
- pdf.js for PDF rendering on both sides
- TanStack Query for data fetching
- Zustand for state management

**Backend:**
- FastAPI (Python, async)
- Pydantic for validation
- SQLAlchemy ORM for database
- Celery + Redis for async job processing
- PostgreSQL for metadata

**External Services:**
- DeepL API for primary translation
- Claude 3.5 Haiku for tone customization
- LlamaParse for scanned PDF OCR (fallback)
- AWS S3 for temporary file storage
- Google OAuth for authentication

**Infrastructure:**
- AWS ECS for containerized deployment
- AWS S3 for file storage
- AWS CloudFront for CDN
- AWS RDS for PostgreSQL
- AWS ElastiCache for Redis
- AWS Lambda for scheduled cleanup jobs

### Processing Pipeline

1. User uploads PDF → Server receives chunked upload → Store temporarily in S3
2. Validate PDF → Extract text + layout with PyMuPDF
3. Translate text → Call DeepL API in batches (parallelized by page)
4. Reconstruct PDF → Use PDFBox to rebuild with translated text
5. Tone customization → Call Claude Haiku with translation + tone description
6. Final PDF → Return to user for download

---

## MVP Implementation Notes

### Phase 1: Core MVP (Weeks 1-3)

**Week 1:**
- Upload flow with Google OAuth
- Basic PDF extraction and rendering
- DeepL translation integration
- Database schema

**Week 2:**
- Side-by-side review interface
- Synchronized highlighting
- Tone customization (presets only initially)

**Week 3:**
- Edit & alternatives workflow
- Download functionality
- Freemium tier enforcement
- Error handling & edge cases
- Testing & bug fixes

### Phase 2: Polish & Launch (Week 4)

- Performance optimization
- UI/UX refinement
- Security audit
- Load testing
- Beta launch

---

## Assumptions & Risks

### Key Assumptions

1. **DeepL quality + Claude tone = better translations** — We assume this combination produces noticeably better results than Google Translate. Validated in beta.

2. **Users will actually use the review feature** — Side-by-side highlighting adds friction. Users must find it valuable enough to use. Validated by metrics.

3. **Freemium → Subscription conversion works** — Users will upgrade after 2 free documents. Pricing must be attractive.

4. **Processing speed is acceptable** — 45-90 seconds is fast enough for users. If users expect <30 seconds, architecture must change.

### Key Risks

1. **Translation Quality Below Expectations**
   - Risk: Users perceive translations as not much better than alternatives
   - Mitigation: Extensive QA before launch, comparison testing with Google/DeepL

2. **Tone Customization Adds Complexity Without Value**
   - Risk: Users find tone selection confusing, underutilize the feature
   - Mitigation: Strong UX for presets, excellent examples, clear explanations

3. **Performance Issues With Large Files**
   - Risk: 100MB PDFs cause timeouts or slow processing
   - Mitigation: Extensive load testing, async architecture, chunked processing

4. **Free → Paid Conversion Low**
   - Risk: Users don't upgrade, freemium doesn't work
   - Mitigation: Generous free tier (2 docs), attractive pricing, clear value messaging

---

## Success Metrics Summary

**MVP Success (Month 1):**
- ✅ 70%+ users rate translation quality as good/excellent
- ✅ 60%+ of users actively use side-by-side review feature
- ✅ 50+ document downloads (paid-tier or free-tier limit reached)
- ✅ NPS 40+
- ✅ No critical bugs blocking usage

**Phase 2 (Months 3-6):**
- 40%+ return user rate (users translate 2+ documents)
- 15%+ subscription conversion rate
- Enterprise feature readiness for Phase 3

---

## Appendix: Functional Requirements Checklist

**Authentication & Users (FR1-10):** ✅ Complete
**Upload & File Handling (FR11-20):** ✅ Complete  
**Language & Source Detection (FR21-30):** ✅ Complete  
**Translation Processing (FR31-40):** ✅ Complete  
**Review Interface (FR41-50):** ✅ Complete  
**Tone Customization (FR51-60):** ✅ Complete  
**Edit & Alternatives (FR61-70):** ✅ Complete  
**Download (FR71-80):** ✅ Complete  
**Session Management (FR81-90):** ✅ Complete  
**Error Handling (FR91-100):** ✅ Complete  

**Total: 100 Functional Requirements documented**

---

**Status:** Ready for Epic Breakdown & UX Design Phase

**Created:** November 14, 2025  
**Track:** Enterprise Method - Greenfield  
**Next:** Epic Breakdown workflow will decompose these FRs into implementable user stories

