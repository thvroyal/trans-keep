# Product Brief: TransKeep

**Date:** November 14, 2025  
**Author:** Roy  
**Project Context:** Greenfield - Individual users first, enterprise roadmap

---

## Executive Summary

**TransKeep** is a premium document translation platform that prioritizes **translation quality** and **user control** through a uniquely focused review experience. Unlike generic translation tools, TransKeep empowers users to understand, customize, and confidently approve translations before downloading.

**Core Promise:** Better translations through better *control*. Users don't just get a translation — they get to review alternatives, customize tone, and refine the result until it's perfect.

**Launch Focus:** Individual users seeking high-quality translations with professional presentation. Enterprise collaboration roadmap built into architecture.

**Key Differentiator:** Side-by-side comparison with synchronized highlighting + tone customization for creative translation = translations that are both accurate AND beautifully expressed.

---

## Core Vision

### Problem Statement

Current translation tools suffer from two fundamental failures:

1. **Quality Gap:** Machine translation produces technically correct but emotionally flat output. A novel translated by Google Translate reads like a machine wrote it — correct grammar, wrong soul.

2. **Verification Burden:** Users have no good way to verify if a translation is correct. They must either:
   - Trust the tool blindly (risky for important documents)
   - Compare source and target manually (tedious, error-prone)
   - Hire professional translators (expensive)

3. **No Customization:** Translation tone is fixed. A user translating a novel can't ask for "lyrical and poetic." A business translator can't request "formal and precise." They get one style: robotic.

**The result:** Users settle for mediocre translations or invest hours of manual review.

### Problem Impact

**For individuals:**
- Students translating academic papers waste hours verifying accuracy
- Novel readers want literary translations, not literal ones
- Language learners can't compare to learn
- Cost: hours of frustration per document

**For enterprises:**
- Technical teams translating documentation face consistency issues
- Marketing teams get translations that don't capture brand voice
- Multiple reviewers have no efficient way to collaborate
- Cost: expensive rework, delays, quality inconsistency

### Why Existing Solutions Fall Short

**Competitors identified in market research:**

- **Adobe Acrobat:** Good format preservation, poor review UX
- **Google Translate:** Fast and cheap, but robotic output
- **DeepL:** High quality, but no review/editing capability
- **Smartcat:** Comprehensive platform, overcomplicated for simple use cases
- **DocTranslator:** Simple but minimal control over output

**Gap Analysis:** No competitor has optimized for *the review and refinement experience* combined with *tone customization*.

### Proposed Solution

**TransKeep** solves this with three integrated capabilities:

**1. Side-by-Side Review with Synchronized Highlighting**
- Original PDF on left, translated version on right
- Hover over any block in either version → highlights corresponding section in both
- Users instantly verify accuracy: "Did my meaning transfer correctly?"
- See formatting preserved in real-time

**2. Tone Customization for Creative Translation**
- Quick-select predefined tones: Formal, Casual, Technical, Creative, Academic
- Custom tone input: "Write like a poet" or "Technical documentation style"
- System re-interprets translation through that lens
- Result: Novel reads beautifully. Technical doc is precise. Marketing copy has brand voice.

**3. Edit & Refine Before Download**
- Click any translation to edit inline
- See alternative translation options (multiple ways to say the same thing)
- Re-translate sections with different tone if needed
- Download only when satisfied

### Key Differentiators

**vs. Generic Translation Tools (Google, DeepL):**
- ✅ Review-centric UX (they're translation engines, not review platforms)
- ✅ Tone customization (they have none)
- ✅ Edit workflow (they don't)

**vs. Professional Platforms (Smartcat, Adobe):**
- ✅ Simple, focused, fast (they're over-engineered)
- ✅ Modern & premium design (they feel enterprise-corporate)
- ✅ Accessible pricing (they're expensive)

**vs. Simple Tools (DocTranslator):**
- ✅ Quality focus (they sacrifice quality for speed)
- ✅ Customization (they're one-size-fits-all)
- ✅ Professional polish (they look basic)

---

## Target Users

### Primary Users: Individuals Seeking Quality

**Persona: The Conscientious Translator**
- Translating for reading/understanding: novels, articles, blogs, academic papers
- Cares deeply about quality and nuance
- Willing to spend a few minutes reviewing to get it right
- Values beautiful, expressive translations over speed
- Comfortable with technology but wants simplicity

**Current Workflow:**
1. Use Google Translate
2. Compare source/target manually (tedious)
3. Get frustrated with flat tone
4. Give up or hire translator

**TransKeep Value:**
- Review is easy and intuitive (synchronized highlighting)
- Tone customization lets them get creative translations
- Download confident the result is good
- Time: 15 minutes instead of hours

**Volume:** High frequency (weekly or more for regular users)

### Secondary Users: Professionals & Enterprises (Future Roadmap)

**Later Focus:** Teams needing collaborative workflows
- Simultaneous editing (multiple people, different sections)
- Consistency management (glossary/terminology auto-apply across document)
- Multi-tenant architecture supports both individual and team workflows

**MVP doesn't include these, but architecture is built to scale.**

### User Journey

**Happy Path for Individual Translating a Novel:**

1. **Upload** — Drag-drop PDF, select target language (Japanese)
2. **Initial Review** — See side-by-side translation, hover over passages to verify
3. **Tone Selection** — Click "Creative" preset to make it more literary
4. **Refine** — Find a passage that reads flat, click alternatives, pick better phrasing
5. **Final Edit** — One paragraph doesn't feel right, click to edit, re-translate with "poetic" tone
6. **Confidence** — Read through, feels good
7. **Download** — Get translated PDF, beautifully formatted

**Time:** 10-20 minutes for satisfaction vs. 1-2 hours with manual comparison

---

## Success Metrics

### Quality First
- **Metric:** Users report translations are better than Google Translate
- **Measurement:** In-app feedback/rating after download
- **Target for MVP:** 80%+ of users rate quality as good or excellent

### Speed Optimization
- **Metric:** Complete translation of 100-page document in under 90 seconds
- **Measurement:** Process time tracking
- **Target for MVP:** Consistent 45-75 second processing

### Cost Efficiency
- **Metric:** Sustainable cost structure allows profitable pricing
- **Calculation:** ~$1.62 cost per 100-page document
- **Pricing:** Free tier (2 docs), then subscription (price TBD based on usage patterns)
- **Target:** Unit economics support profitability at any reasonable subscription tier

### User Satisfaction
- **Metric:** Repeat usage rate
- **Target:** 60%+ of users translate 3+ documents in first 30 days

---

## MVP Scope

### Core Features (Required for Launch)

**1. Document Upload & Processing**
- Drag-drop PDF upload (up to 100MB)
- Support: English → Japanese, Vietnamese (MVP languages)
- Auto-detect quality: digital PDF vs. scanned

**2. Side-by-Side Review Interface**
- Left: Original PDF rendered
- Right: Translated PDF rendered
- Synchronized scrolling
- Hover highlighting (block-level)

**3. Tone Customization**
- Predefined tones: Formal, Casual, Technical, Creative, Academic
- Custom tone input field for specific requests
- One-click tone reapplication

**4. Edit & Alternatives Workflow**
- Click any translated section to edit inline
- Show 2-3 alternative phrasing options
- Re-translate specific sections with custom tone
- Real-time preview

**5. Download & Export**
- Download translated PDF
- Original formatting preserved
- High-quality output

**6. Freemium Model**
- Free tier: 2 documents/month
- Upgrade prompt after 2 free documents
- Subscription tier (pricing TBD)

### Out of Scope for MVP

- ❌ Collaborative editing (enterprise feature, Phase 2)
- ❌ Glossary/terminology databases (enterprise feature, Phase 2)
- ❌ Mobile native apps (web-first only)
- ❌ DOCX, PPTX support (Phase 2 roadmap)
- ❌ 60+ language support (start with 3 high-value pairs)
- ❌ User accounts/history (can add in Phase 2)
- ❌ Advanced analytics

### MVP Success Criteria

- ✅ Translates documents without format loss
- ✅ Translation quality noticeably better than free alternatives
- ✅ Review experience is intuitive (no manual side-by-side comparison needed)
- ✅ Tone customization produces visibly different results
- ✅ Users can edit and see changes immediately
- ✅ Download workflow is one-click
- ✅ Processing time: <90 seconds for 100-page document
- ✅ Users rate experience as professional/premium

### Future Vision (Phase 2+)

**Phase 2 - Enterprise Collaboration:**
- Simultaneous editing (real-time collaboration)
- Glossary/terminology management with auto-apply
- User accounts, project tracking
- Comment/suggestion workflows
- Version history

**Phase 3 - Format Expansion:**
- DOCX translation with preservation
- PPTX translation with slide handling
- HTML, markdown support

**Phase 3 - Scale & Intelligence:**
- 30+ language pairs
- Domain-specific models (medical, legal, technical)
- Translation memory integration
- Custom glossary upload from user's terminology

---

## Technical Preferences

**Platform:** Web-first (desktop & tablet responsive)
- Not mobile-native initially
- Progressive enhancement for mobile web

**Architecture:** Multi-tenant from Day 1
- Supports individual users at launch
- Enterprise features can be enabled later
- Single codebase, different feature tiers

**Tech Stack:**
- **Frontend:** React 18 + shadcn/ui (modern & premium aesthetic)
- **Backend:** FastAPI (Python, async, high-performance)
- **PDF Processing:** PyMuPDF (fast extraction) + LlamaParse (fallback for scanned)
- **Translation:** DeepL (primary), Claude Haiku (tone customization)
- **Infrastructure:** AWS S3, CloudFront, serverless processing

**Design Philosophy:**
- Modern & premium (Figma-like, not corporate)
- Confidence through design quality
- Minimalist interface, maximum control

---

## Market & Business Context

### Market Opportunity

From market research (docs/research.md):
- Document translation market growing steadily
- Enterprise globalization driving demand
- AI/LLM adoption accelerating
- Format preservation recognized as critical pain point
- 7 competitors identified with varying approaches

### Competitive Positioning

**TransKeep's unique position:**
- Only tool optimizing for *translation review experience*
- Only tool offering *tone customization for creative translation*
- Modern, premium design vs. corporate-looking competitors
- Accessible to individuals (vs. enterprise-only tools)
- Simple focus vs. over-engineered platforms

### Go-to-Market Strategy

**Phase 1 (MVP Launch):**
- Target: Individual translators, language learners, novel readers
- Channels: Product Hunt, Reddit (r/languagelearning), language forums
- Messaging: "Translation that reads like a human wrote it"
- Freemium model drives initial adoption

**Phase 2 (Months 3-6):**
- Expand language support based on user demand
- Introduce enterprise features
- Target: Translation agencies, tech companies
- Messaging: "Professional translation review for teams"

---

## Timeline

**MVP Launch:** 1 month from now
- Research phase: ✅ Complete
- Product Brief: ✅ Complete (this document)
- PRD & Architecture: Next (1 week)
- Development sprint: 2-3 weeks
- Beta & launch prep: 1 week

**Beta Testing:** Post-MVP
- Internal testing with individual users
- Gather feedback on review UX
- Optimize tone customization quality

**Full Launch:** Post-beta refinement

---

## Risks & Assumptions

### Critical Assumptions

1. **DeepL quality is sufficient** — We're assuming DeepL's translation quality + Claude tone adjustment = user satisfaction
2. **Tone customization adds real value** — Users will actually use this feature and prefer it
3. **Review UX matters enough** — Side-by-side comparison justifies premium positioning
4. **Individual market can sustain** — Freemium → subscription model works for personal users

### Key Risks

1. **Translation Quality Perception** — If users find translations worse than expected, positioning fails
   - *Mitigation:* Extensive testing before launch, clear comparison with alternatives
   
2. **Tone Customization Complexity** — If users find tone selection confusing, feature underutilized
   - *Mitigation:* Strong UX with presets, clear examples, contextual help

3. **Competitive Response** — Google/DeepL add review UX features quickly
   - *Mitigation:* Focus on speed to market, build community, differentiate on design quality

4. **Processing Performance** — 100MB PDFs cause timeouts or slow processing
   - *Mitigation:* Extensive load testing, implement chunked processing, async architecture

---

## Vision for 2-Year Success

**In 24 months, TransKeep has:**

✅ Become the go-to tool for individuals wanting high-quality translations
✅ Proven that review + tone customization are compelling features
✅ Expanded to 10-15 language pairs based on user demand
✅ Attracted 10K-50K active individual users
✅ Refined enterprise features for Phase 2 enterprise launch
✅ Maintained profitability or clear path to profitability
✅ Built a reputation for "the translation tool that respects your document and your time"

**The measure of success:** Users say "TransKeep is the best way to translate a document *and be confident in the result.*"

---

## Supporting Materials

**Related Documents:**
- `docs/research.md` — Comprehensive market, competitive, user, and technical research
- `docs/technical-refinements.md` — Detailed technical decisions and architecture
- `docs/tech-decisions-summary.txt` — Quick reference for tech decisions

---

_This Product Brief captures TransKeep's strategic vision and positioning._

_It reflects a focus on quality, user control, and beautiful design._

_Next: PRD workflow will translate this vision into detailed feature specifications and user stories._

---

**Created:** November 14, 2025  
**Status:** Ready for PRD phase

