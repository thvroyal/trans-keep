# Epic 3: UI Polish & Refinement - Tech Stack & Architecture

**Epic:** 3  
**Title:** UI Polish & Refinement ✨  
**Stories:** 3.1 - 3.5  
**Duration:** 5 days (Dec 16-20)  
**Status:** contexted  
**Created:** November 15, 2025

---

## Overview

Implement the hero review experience with dual PDF viewer, tone customization with AI, edit & alternatives workflow, PDF download with edits, and comprehensive error handling.

---

## 📦 Tech Stack by Component

### **PDF Rendering Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **PDF Viewer** | pdf.js | 4.x | Cross-browser PDF rendering | Story 3.1 |
| **Canvas Rendering** | HTML5 Canvas | Built-in | GPU-accelerated PDF display | Story 3.1 |
| **Virtualization** | React Virtual | 10.x | Render only visible pages | Story 3.1 |
| **Zoom Controls** | Custom UI | - | User-controlled zoom levels | Story 3.1 |
| **Page Navigation** | Zustand store | - | Share page state between viewers | Story 3.1 |

### **UI Component Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Components** | shadcn/ui | Latest | Pre-built, accessible components | Story 3.1-3.5 |
| **Progress Bar** | shadcn/ui Progress | - | Visual progress indicator | Story 3.1 |
| **Dialog/Modal** | shadcn/ui Dialog | - | Modals for edits & alternatives | Story 3.3 |
| **Button Variants** | shadcn/ui Button | - | Consistent button styling | All stories |
| **Card Layouts** | shadcn/ui Card | - | Content containers | All stories |
| **Input Fields** | shadcn/ui Input | - | Text editing interface | Story 3.3 |

### **Tone Customization Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **LLM** | Claude Haiku API | Latest | Fast, cost-effective tone customization | Story 3.2 |
| **Client** | Anthropic Python | Latest | Official Claude API client | Story 3.2 |
| **Frontend Hook** | Custom React Hook | - | Tone selector state management | Story 3.2 |
| **Streaming** | Server-Sent Events | - | Real-time tone customization | Story 3.2 |
| **Caching** | Redis | 7 | Cache tone results (24h) | Story 3.2 |
| **Cost Tracking** | Custom logging | - | Track Claude API costs | Story 3.2 |

### **Edit & Alternatives Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **State Management** | Zustand | Latest | In-memory edit tracking | Story 3.3 |
| **Block Mapping** | JavaScript Map | Built-in | block_id → edited_text | Story 3.3 |
| **Alternatives Gen** | Claude API | Latest | Generate 2-3 alternatives | Story 3.3 |
| **Text Editor** | Contenteditable | Built-in | Inline text editing | Story 3.3 |
| **Diff Highlighting** | diff-match-patch | Latest | Show before/after changes | Story 3.3 |

### **PDF Reconstruction Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **PDF Library** | PyMuPDF | 1.23+ | Reconstruct PDF with new text | Story 3.4 |
| **Reconstruction** | Custom function | - | Apply edits to final PDF | Story 3.4 |
| **Storage** | AWS S3 | - | Store final PDF | Story 3.4 |
| **Download** | Pre-signed URL | - | Secure, temporary download link | Story 3.4 |
| **CDN** | CloudFront | - | Fast PDF delivery | Story 3.4 (prod) |

### **Error Handling Stack**

| Component | Technology | Version | Why | Usage |
|-----------|------------|---------|-----|-------|
| **Error Boundaries** | React Error Boundary | 18+ | Catch component errors | Story 3.5 |
| **Retry Logic** | Custom hook | - | Exponential backoff retry | Story 3.5 |
| **Network Status** | Navigator.onLine | Built-in | Detect connection status | Story 3.5 |
| **Fallback Translations** | Google Translate API | - | Fallback if DeepL unavailable | Story 3.5 |
| **User Feedback** | Toast notifications | shadcn/ui | Non-blocking error messages | Story 3.5 |

---

## 🎨 Epic 3 Story & Tech Stack Mapping

### **Story 3.1: Side-by-Side Review Panel (Hero)**
```
Technologies:
├── pdf.js (dual PDF rendering)
├── React Virtualization (large PDFs)
├── Zustand (scroll synchronization)
├── HTML5 Canvas (rendering)
├── Tailwind CSS (responsive layout)
└── Hover highlighting (JavaScript)
```

**Key Files:**
- `frontend/src/components/ReviewPanel.tsx` - Main component
- `frontend/src/components/PDFViewer.tsx` - PDF renderer
- `frontend/src/hooks/useSyncScroll.ts` - Scroll sync
- `frontend/src/hooks/useHoverHighlight.ts` - Hover mapping

**Data Structure:**
```javascript
// Block mapping for highlighting
const blockMapping = {
  "original_block_1": "translated_block_1",
  "original_block_2": "translated_block_2",
  // ...
}

// Scroll position state
const [scrollPos, setScrollPos] = useState({
  left: 0,
  right: 0,
  synced: true
})
```

### **Story 3.2: Tone Customization UI & Logic**
```
Technologies:
├── React UI (ToneSelector component)
├── Claude API (tone re-translation)
├── Zustand (tone selection state)
├── shadcn/ui (UI components)
├── Before/After comparison UI
└── Cost display
```

**Key Files:**
- `frontend/src/components/ToneSelector.tsx` - UI component
- `backend/app/services/tone_service.py` - Claude integration
- `backend/app/routers/translation.py` - Tone endpoint

**Tone Presets:**
```javascript
const TONE_PRESETS = [
  { id: 'professional', label: 'Professional', description: 'Formal business tone' },
  { id: 'casual', label: 'Casual', description: 'Friendly, conversational' },
  { id: 'technical', label: 'Technical', description: 'For documentation' },
  { id: 'creative', label: 'Creative', description: 'For marketing' },
  { id: 'custom', label: 'Custom', description: 'User-defined tone' }
]
```

### **Story 3.3: Edit & Alternatives Workflow**
```
Technologies:
├── Zustand (edit tracking store)
├── React inline editor (EditPanel)
├── Claude API (alternatives)
├── Diff highlighting
├── Re-translation with tone
└── In-memory persistence
```

**Key Files:**
- `frontend/src/components/EditPanel.tsx` - Edit interface
- `frontend/src/hooks/useEditTracking.ts` - Zustand store
- `backend/app/routers/alternatives.py` - Alternatives endpoint

**Edit State:**
```javascript
const editStore = {
  edits: new Map([
    ["block_id_1", "user's edited translation"],
    ["block_id_5", "another edit"]
  ]),
  
  addEdit: (blockId, text) => { /* ... */ },
  removeEdit: (blockId) => { /* ... */ },
  clearAll: () => { /* ... */ },
  getEdits: () => Map
}
```

### **Story 3.4: PDF Download Endpoint**
```
Technologies:
├── FastAPI endpoint (GET /download/{job_id})
├── PyMuPDF (PDF reconstruction)
├── In-memory edits (Zustand → backend)
├── S3 upload (final PDF)
├── Pre-signed URL generation
└── CloudFront CDN (prod)
```

**Key Files:**
- `backend/app/routers/download.py` - Download endpoint
- `backend/app/services/pdf_reconstruction.py` - Reconstruction
- `frontend/src/hooks/useDownload.ts` - Download UI

**Request/Response:**
```javascript
// Frontend sends edits
POST /api/v1/download/{job_id}
{
  "edits": {
    "block_id_1": "edited text",
    "block_id_5": "another edit"
  }
}

// Backend returns
{
  "download_url": "https://cloudfront.../file.pdf?expires=...",
  "expires_in": 3600
}
```

### **Story 3.5: Error Handling & Edge Cases**
```
Technologies:
├── React Error Boundaries (component errors)
├── Network retry logic (exponential backoff)
├── Fallback APIs (Google Translate)
├── Toast notifications (user feedback)
├── Connection status monitoring
├── Graceful degradation
└── Comprehensive logging
```

**Key Files:**
- `frontend/src/components/ErrorBoundary.tsx` - Error catching
- `frontend/src/utils/retry.ts` - Retry utility
- `frontend/src/utils/fallbacks.ts` - Fallback logic
- `backend/app/middleware/error_handler.py` - Error middleware

**Error Handling Strategy:**
```javascript
// Retry with exponential backoff
async function retryWithBackoff(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      const delay = Math.pow(2, i) * 1000
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
}

// API fallback
async function translateWithFallback(text) {
  try {
    return await deeplTranslate(text)  // Primary
  } catch (error) {
    console.warn('DeepL failed, using fallback', error)
    return await googleTranslate(text)  // Fallback
  }
}
```

---

## 🗄️ Frontend State Management (Zustand)

### **Global App Store**
```typescript
interface AppStore {
  // User & Auth
  user: User | null
  isAuthenticated: boolean
  
  // Current Translation
  currentJob: TranslationJob | null
  currentTranslation: Translation | null
  
  // PDF Display
  leftPdfFile: PDFDocument | null
  rightPdfFile: PDFDocument | null
  currentPage: number
  scrollSynced: boolean
  
  // Tone Selection
  selectedTone: string
  customTone: string | null
  toneOptions: TonePreset[]
  
  // Edits
  edits: Map<string, string>  // block_id → edited_text
  
  // UI State
  showToneSelector: boolean
  showEditPanel: boolean
  downloadInProgress: boolean
  
  // Actions
  setUser: (user: User) => void
  setCurrentJob: (job: TranslationJob) => void
  addEdit: (blockId: string, text: string) => void
  removeEdit: (blockId: string) => void
  clearAllEdits: () => void
  setSelectedTone: (tone: string) => void
  setScrollSynced: (synced: boolean) => void
}

// Create store
export const useAppStore = create<AppStore>((set) => ({
  // Initial state
  user: null,
  isAuthenticated: false,
  currentJob: null,
  edits: new Map(),
  
  // Actions
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  addEdit: (blockId, text) => set((state) => {
    const newEdits = new Map(state.edits)
    newEdits.set(blockId, text)
    return { edits: newEdits }
  }),
  // ... more actions
}))
```

---

## 🎯 Success Criteria for Epic 3

**All stories in Epic 3 must satisfy:**

- ✅ Dual PDF rendering side-by-side
- ✅ Synchronized scrolling works smoothly
- ✅ Hover highlighting responsive (<50ms)
- ✅ Responsive design (desktop, tablet, mobile)
- ✅ Tone presets apply instantly
- ✅ Alternatives display correctly
- ✅ Edits tracked in-memory
- ✅ PDF download with edits applied
- ✅ Error messages clear and actionable
- ✅ Large PDFs (500 pages) perform well
- ✅ Network error recovery working
- ✅ API fallbacks functional
- ✅ All tests passing
- ✅ No memory leaks with large PDFs

---

## 📚 External Resources

- [pdf.js Docs](https://mozilla.github.io/pdf.js/)
- [React Virtual Docs](https://tanstack.com/virtual/latest)
- [Zustand Docs](https://github.com/pmndrs/zustand)
- [Anthropic Claude API](https://anthropic.com/docs)
- [Tailwind CSS](https://tailwindcss.com)

---

**Epic 3 Tech Stack Status:** ✅ **CONTEXTED**

All technologies identified for Stories 3.1-3.5.
Ready for implementation.

**Created:** November 15, 2025  
**Last Updated:** November 15, 2025

