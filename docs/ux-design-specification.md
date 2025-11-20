# TransKeep - UX Design Specification

**Created:** November 14, 2025  
**Author:** Roy  
**Platform:** Web (React + shadcn/ui)  
**Aesthetic:** Figma (modern, minimal, spacious, clean)  
**Emotional Driver:** Confidence  

---

## Executive Summary

**TransKeep UX Philosophy:** "Confidence through clarity and control"

Users feel confident in their translations through:
1. **Crystal-clear side-by-side review** — See both versions simultaneously with synchronized highlighting
2. **Obvious tone control** — Quick presets + custom options, instant visual feedback
3. **Effortless editing** — Click to edit, see alternatives, preview changes immediately
4. **Professional polish** — Modern, spacious design that feels premium and trustworthy

**Design Aesthetic:** Figma-inspired
- Minimal, purposeful interface (every element earns its space)
- Generous whitespace (premium feel)
- Clean typography with clear hierarchy
- Intuitive interactions (no learning curve)
- Confidence-building visual feedback

---

## 1. Design System Foundation

### 1.1 Design System Choice: shadcn/ui + Custom Tailwind

**Why shadcn/ui:**
- ✅ Built on Radix UI primitives (accessible by default)
- ✅ Headless components (full customization)
- ✅ Tailwind CSS based (modern, lightweight)
- ✅ Figma aesthetic achievable (minimal, clean)
- ✅ Perfect for React developers

**Customization for TransKeep:**
- Use shadcn/ui base components
- Extend with custom Tailwind classes for spacing, typography, colors
- Create TransKeep-specific component variants (e.g., "confident button", "review panel")

### 1.2 Key Design Principles

**1. Confidence First**
- Every interaction should reinforce user confidence in their translation
- Visual hierarchy makes the important obvious
- Clear feedback confirms actions happened
- No ambiguity or confusion

**2. Focus on Core Experience**
- Side-by-side review dominates the screen
- All other features (tone, edit, download) support the review
- Every pixel should aid the review experience

**3. Spacious & Breathable**
- Generous margins and padding (Figma style)
- Don't pack the interface tightly
- White space is a design element, not wasted space
- 24px base unit for consistent spacing

**4. Modern Minimalism**
- Remove anything decorative that doesn't serve function
- Clean lines, simple shapes
- Subtle interactions (no jarring animations)
- Typography does the heavy lifting

---

## 2. Core User Experience

### 2.1 The Side-by-Side Review Experience (Hero Flow)

**THIS IS THE SOUL OF TRANSKEEP.**

The side-by-side review interface must:
- ✅ Occupy 80%+ of the viewport (it's the main event)
- ✅ Show original PDF on left, translated on right
- ✅ Synchronized scrolling (both move together by default)
- ✅ Hover highlighting: When user hovers over any block in left, right highlights corresponding section (and vice versa)
- ✅ Visual confidence: The highlighting is clear but not jarring (use accent color, not neon)
- ✅ Responsive: Stacks vertically on tablet/mobile with tab toggle

**Why this matters:**
Users instantly see if translation captured the meaning. No manual side-by-side comparison needed. This is what they can't get anywhere else.

### 2.2 Interaction Model: "Click → Change → See Result"

TransKeep's entire UX follows one pattern:

**1. Click any element** (tone preset, text block, edit button)
**2. Change happens** (tone applied, edit panel opens, alternative shown)
**3. See result immediately** (translation updates in real-time, or preview appears)
**4. No confirmation dialogs** (removes friction, confidence through instant feedback)

---

## 3. Visual Design System

### 3.1 Color Palette (Figma Inspired)

**Primary Colors:**

| Color | Usage | Value |
|-------|-------|-------|
| **Confidence Blue** | Primary brand, highlights, focus | `#2563EB` |
| **Neutral 50** | Backgrounds, light surfaces | `#F9FAFB` |
| **Neutral 100** | Cards, panels, subtle backgrounds | `#F3F4F6` |
| **Neutral 900** | Text, dark elements | `#111827` |
| **Neutral 600** | Secondary text, disabled states | `#4B5563` |

**Accent Colors:**

| Color | Usage | Value |
|-------|-------|-------|
| **Success Green** | Successful uploads, completed states | `#10B981` |
| **Warning Orange** | Large files, warnings | `#F59E0B` |
| **Error Red** | Errors, validation failures | `#EF4444` |
| **Hover Highlight** | Hover feedback in review | `#DBEAFE` (light blue) |

**Why These Colors:**
- **Confidence Blue**: Trustworthy, professional, used sparingly for impact
- **Neutral palette**: Modern, clean, Figma-like
- **Highlight color**: Subtle but clear (light blue, not neon)
- **Status colors**: Clear feedback (green = good, orange = caution, red = error)

### 3.2 Typography System

**Font Stack:**
```
System fonts for fast loading & modern feel:
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", 
            "Oxygen", "Ubuntu", "Cantarell", "Fira Sans", "Droid Sans", 
            sans-serif;
```

**Typography Scale (using Tailwind):**

| Level | Size | Weight | Usage |
|-------|------|--------|-------|
| **Page Title** | 32px / 2rem | 700 | "Upload Document" headings |
| **Section Title** | 24px / 1.5rem | 700 | "Tone Selection", "Edit Translation" |
| **Body Text** | 16px / 1rem | 400 | Main content, instructions |
| **Small Text** | 14px / 0.875rem | 400 | Metadata, hints, secondary info |
| **Caption** | 12px / 0.75rem | 500 | Labels, character counts |

**Why this scale:**
- 16px minimum for accessibility
- Minimal scale (4 levels) = clean, consistent
- Hierarchy is obvious without being dramatic

### 3.3 Spacing System (24px Base Unit)

```
Spacing scale (multiples of 4px, base unit 24px):
- xs: 4px (micro-spacing)
- sm: 8px
- md: 12px
- base: 16px (not used much)
- lg: 24px (standard)
- xl: 32px (large sections)
- 2xl: 48px (major breaks)
- 3xl: 64px (page-level spacing)
```

**Application:**
- Component padding: 16px (inside buttons, panels)
- Card spacing: 24px (between cards)
- Major sections: 48px (between main areas)
- Page edges: 24px minimum

### 3.4 Shadows & Depth (Subtle, Figma-like)

**Shadow System:**

| Level | Shadow | Usage |
|-------|--------|-------|
| **Hover** | `0 2px 4px rgba(0,0,0,0.05)` | Subtle lift on hover |
| **Card** | `0 1px 3px rgba(0,0,0,0.1)` | Floating panels, modals |
| **Floating** | `0 10px 15px rgba(0,0,0,0.1)` | Dropdowns, important modals |

**Why subtle:**
- Modern aesthetic doesn't need heavy shadows
- Subtlety = confidence (not trying too hard)
- Focus is on content, not design effects

---

## 4. Design Direction & Key Screens

### 4.1 Core User Flows

**FLOW 1: Upload & Prepare**

```
┌─────────────────────────────────────┐
│     Upload Document Screen          │
│                                     │
│    [Drag & drop zone - large]       │
│    "Drop PDF here or click"         │
│                                     │
│    [Language selector]              │
│    "English → Japanese"             │
│                                     │
│    [Upload button - prominent]      │
└─────────────────────────────────────┘
           ↓
    [Processing with progress]
           ↓
┌─────────────────────────────────────┐
│   Translation Processing Screen     │
│                                     │
│  📄 filename.pdf                    │
│  Language: English → Japanese       │
│                                     │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░     │
│  Page 1 of 45 • Est. 60 seconds    │
│                                     │
│  Current progress:                  │
│  ✓ Extraction   [1 sec]            │
│  ⊙ Translation  [Processing...]    │
│    Tone apply                       │
│    Reconstruction                   │
└─────────────────────────────────────┘
```

**FLOW 2: Review (THE HERO FLOW)**

```
┌──────────────────────────────────────────────────────┐
│  TransKeep - Review & Refine                         │
├────────┬──────────────────────────────────────┬─────┤
│ UPLOAD │ ⊗ REVIEW & REFINE                   │ ⊗ ⊗│
└────────┴──────────────────────────────────────┴─────┘
│                                                       │
│  ┌─────────────────────┬──────────────────────┐    │
│  │    ORIGINAL PDF     │  TRANSLATED PDF      │    │
│  │                     │                      │    │
│  │ Lorem ipsum dolor   │ [Lorem ipsum...]     │    │
│  │ sit amet,           │ [sit amet...]        │    │
│  │ consectetur...      │ [consectetur...]     │    │
│  │                     │                      │    │
│  │ ┌─────────────────┐ │ ┌──────────────────┐│    │
│  │ │ [Table/Image]   │ │ │ [Table/Image]    ││    │
│  │ └─────────────────┘ │ └──────────────────┘│    │
│  │                     │                      │    │
│  │ [Hover = highlight] │ [Same highlight]     │    │
│  └─────────────────────┴──────────────────────┘    │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ TONE & REFINEMENT PANEL (collapsible)        │ │
│  ├──────────────────────────────────────────────┤ │
│  │ Current Tone: Creative                       │ │
│  │ ○ Formal  ○ Casual  ○ Technical            │ │
│  │ ◉ Creative ○ Academic                       │ │
│  │                                              │ │
│  │ Custom Tone: _______________                │ │
│  │ [Apply Tone button]                          │ │
│  │                                              │ │
│  │ [Edit Selected Text] [Download] buttons     │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
└────────────────────────────────────────────────────┘
```

**Key Interactions on Review Screen:**

1. **Synchronized Scrolling** (Default ON)
   - Both panels scroll together
   - User can toggle OFF if they want independent scrolling
   - Toggle button in top-right corner

2. **Hover Highlighting** (THE STAR FEATURE)
   - User hovers over any block in left panel
   - Right panel's corresponding block highlights (light blue)
   - Hover effect uses accent color: `#DBEAFE` (very light)
   - Text remains readable (not overdone)

3. **Tone Selection** (Quick & Obvious)
   - 5 preset buttons displayed as options (not dropdown)
   - Current tone has visual indicator (filled vs outline)
   - Custom tone input below presets (secondary but visible)
   - Clicking preset immediately applies (no confirmation)

4. **Edit Workflow** (Click → Edit → Apply)
   - Click any text block → inline edit panel appears below
   - See 2-3 alternatives (light gray, selectable)
   - Type to edit or click alternative
   - "Apply" button confirms change
   - Translation updates immediately in right panel

---

### 4.2 Screen Specifications

**SCREEN 1: Upload Screen**

```
Layout: Centered column, max-width 600px

Header:
- Logo + "TransKeep" (left)
- Account menu (right)
- Page title: "Upload Document" (center, below nav)

Content:
- Large drop zone (300px height, light background)
  - Center icon: upload/document icon
  - Text: "Drop PDF here or click to browse"
  - Subtext: "Supports PDF up to 100MB"
  
- Language selector (full width, below drop zone)
  - Label: "Translate to:"
  - Dropdown showing: "Japanese" (selected), "Vietnamese"
  - Right side: flag or language icon
  
- Action buttons (full width, spaced)
  - Primary button: "Upload" (Confidence Blue)
  - Secondary: "Need help?" link

Footer:
- Progress indicator (if applicable): "2 of 2 documents used this month"
```

**SCREEN 2: Processing Screen**

```
Layout: Centered card

Title: "Translating Your Document..."

Card contents:
- File info
  - Icon: document type
  - Filename: "novel-excerpt.pdf"
  - Size: "2.4 MB"
  - Language pair: "English → Japanese"

Progress section:
- Large progress bar (60% width)
- Percentage: "Page 12 of 45"
- Estimated time: "Est. 45 sec remaining"

Step-by-step breakdown (below progress):
- ✓ PDF Extraction (completed, green checkmark)
- ⊙ Translation (in progress, spinning icon)
- ○ Tone Customization (pending)
- ○ Final Assembly (pending)

Status message: "Extracting and translating text..."
```

**SCREEN 3: Review Screen (The Hero)**

```
Layout: Full viewport, two-column

TOP BAR (fixed):
- Left: Upload new document button
- Center: Breadcrumb/page indicator
- Right: Settings menu, Account

MAIN CONTENT (two-column, full height):

Left Column (50%):
- Title: "Original PDF"
- PDF viewer with native scroll
- Padding: 24px

Right Column (50%):
- Title: "Translated PDF"
- PDF viewer with native scroll
- Padding: 24px

BOTTOM PANEL (collapsible, above fold):
- Title: "Refine Your Translation"
- Tabs: "Tone" | "Edit" | "Settings"

TONE TAB (default open):
- Tone Presets (horizontal buttons)
  - Formal | Casual | Technical | Creative | Academic
  - Currently selected highlighted with background color
- Custom Tone Input
  - Text field: "Or describe the tone you want..."
  - "Apply Tone" button
- Action buttons at bottom
  - "Edit Selected Text" (if block selected)
  - "Download" (prominent, Confidence Blue)

EDIT TAB:
- Selected text preview (if any)
- Inline editor
- Alternatives (light gray buttons)
- "Apply Edit" button

Responsive (Tablet):
- Stacks to tabs: "Original" | "Translated"
- Bottom panel takes full width when expanded
```

---

## 5. User Journey Flows

### 5.1 Happy Path: Review & Download

```
1. UPLOAD
   User drags PDF → Selects language → Clicks Upload
   [Feels: Simple, inviting]

2. PROCESSING
   User sees progress bar
   System processes document
   [Feels: Reassured (clear progress)]

3. REVIEW
   Translation complete
   User sees side-by-side view
   Original on left, translated on right
   [Feels: Relieved ("I can verify this!")]

4. VERIFY WITH HOVER
   User hovers over original passages
   Corresponding translation highlights
   User confirms accuracy
   [Feels: Confident ("Yes, this captured the meaning")]

5. TONE ADJUSTMENT (Optional)
   User sees translation reads flat/robotic
   Clicks "Creative" tone preset
   Translation re-applies with tone
   [Feels: Delighted ("Now it reads beautifully!")]

6. DOWNLOAD
   User clicks "Download"
   Translated PDF downloads
   [Feels: Satisfied ("Mission accomplished")]
```

### 5.2 Alternative Path: Edit & Re-Translate

```
1-4. SAME AS ABOVE (Upload → Review)

5. EDIT FLOW
   User hovers and finds one section needs work
   Clicks that section → Edit panel opens
   Sees original text + alternatives
   Picks better alternative or types own translation
   [Feels: Empowered ("I have control")]

6. RE-TRANSLATE
   User wants to change tone for specific section
   Selects "Re-translate with tone"
   System applies custom tone to just that section
   [Feels: Masterful ("I can fine-tune this")]

7. DOWNLOAD
   User clicks "Download"
   Translated PDF with all edits applied
   [Feels: Proud ("This is MY translation")]
```

---

## 6. Component Library & Design Patterns

### 6.1 shadcn/ui Components Used

**Navigation & Layout:**
- `Button` (with variants: primary, secondary, ghost)
- `Tabs` (for screen sections)
- `Separator` (dividers between sections)

**Forms & Input:**
- `Input` (text fields for language selection, custom tone)
- `Select` (language dropdown)
- `Textarea` (custom tone input)

**Feedback & Status:**
- `Progress` (upload/translation progress bar)
- `Alert` (errors, warnings)
- `Toast` (download confirmation, small notifications)

**Overlays:**
- `Dialog` (modals for settings, help)
- `Popover` (quick info tooltips)

**Data Display:**
- `Card` (panels for tone selection, edit area)
- `Badge` (status indicators, tone labels)

### 6.2 Custom Components for TransKeep

**ReviewPanel**
- Two-column PDF viewer with synchronized scroll
- Hover highlighting on both sides
- Custom implementation (uses pdf.js for rendering)

**ToneSelector**
- 5 preset buttons in horizontal layout
- Custom input field below
- Visual indicator of current tone
- Connected to tone application logic

**EditPanel**
- Inline text editor
- Alternative suggestions displayed
- "Apply" confirmation
- Real-time preview of changes

**ProgressIndicator**
- Step-by-step breakdown (Extract → Translate → Tone → Assemble)
- Visual progress bar
- Estimated time remaining
- Status message updates

---

## 7. Interaction Patterns & Behaviors

### 7.1 Consistency Rules

**Click Behavior:**
- Every interactive element responds to click
- Click feedback is immediate (no delay)
- State change is obvious (highlight, color change, etc.)
- No multi-step confirmations (reduce friction)

**Hover Behavior:**
- Buttons show subtle highlight on hover
- PDF text blocks show highlighting in paired viewer
- Cursor changes to pointer on clickable elements
- Hover feedback is subtle (not jarring)

**Error Handling:**
- Errors displayed in context (not modal pop-ups)
- Clear explanation of what went wrong
- Actionable fix suggested ("File too large. Try under 100MB")
- Error states use Warning Orange (`#F59E0B`)

**Loading States:**
- Spinner or progress bar visible
- User always knows something is happening
- Time estimates shown ("About 60 seconds")
- Can't proceed until complete (prevents confusion)

**Successful States:**
- Green checkmark or "Success" message
- Uses Success Green (`#10B981`)
- Clear next action (e.g., "Download your translation")

### 7.2 Micro-Interactions

**Tone Preset Selection:**
- Clicked preset shows filled background
- Non-selected presets show outline
- Smooth transition (200ms)
- Immediately applies (no loading)

**PDF Hover Highlighting:**
- Light blue highlight appears on hover
- Highlight spans corresponding text
- Works bidirectionally (left hover → right highlights, and vice versa)
- Highlight is readable (not overpowering)

**Edit Mode Entry:**
- Click text block → edit panel slides up from bottom
- Original text selected/highlighted
- Alternatives appear with subtle animation
- "Apply" button is the clear call-to-action

**Download Completion:**
- Success toast appears: "Downloaded: filename.pdf"
- Toast auto-dismisses after 3 seconds
- File actually downloaded to device

---

## 8. Responsive Design & Accessibility

### 8.1 Responsive Breakpoints

**Desktop (1024px+)**
- Two-column side-by-side review
- All features visible at once
- Full-width panels
- ✅ Optimal experience

**Tablet (768px - 1024px)**
- Two-column still possible but cramped
- May need scrolling within panels
- Tone panel below PDFs
- Alternative: Tab toggle between Original/Translated

**Mobile (< 768px)**
- Single column design
- Tab toggle: "Original" | "Translated"
- Full-screen each view
- Tone panel takes full width when expanded
- Download button always visible (sticky bottom)
- ⚠️ MVP doesn't optimize for mobile, but responsive framework ready for Phase 2

### 8.2 Accessibility (WCAG 2.1 AA)

**Keyboard Navigation:**
- Tab through all interactive elements
- Focus indicator always visible (blue outline, 2px)
- Enter/Space to activate buttons
- Arrow keys to navigate tone presets
- Escape to close modals
- No keyboard traps

**Screen Reader Support:**
- All buttons labeled with `aria-label` or visible text
- Form inputs have associated labels
- Tone presets announced as group with ARIA roles
- Error messages announced with `role="alert"`
- Loading states announced ("Translating, please wait")
- PDF viewers labeled properly for accessibility

**Color Contrast:**
- All text meets 4.5:1 contrast ratio
- Accent highlights have sufficient contrast
- Color not the only indicator (text labels + icons)
- Error states use text + Warning Orange color

**Visual Design:**
- Minimum 16px font size for body text
- Line height minimum 1.5 (readable)
- Touch targets 44x44px minimum (for mobile, Phase 2)
- Focus states visible and obvious
- No flashing or auto-playing content

---

## 9. Implementation Guidance for Developers

### 9.1 Component Architecture

**React Component Structure:**

```
App/
├─ Layout/
│  ├─ Navigation
│  └─ Footer
├─ Pages/
│  ├─ Upload.tsx
│  ├─ Processing.tsx
│  └─ Review.tsx (THE HERO)
├─ Components/
│  ├─ ReviewPanel.tsx (custom PDF viewer)
│  ├─ ToneSelector.tsx (tone presets + input)
│  ├─ EditPanel.tsx (inline editor)
│  ├─ ProgressIndicator.tsx
│  └─ [shadcn/ui components]
├─ Hooks/
│  ├─ usePDFViewer
│  ├─ useToneApplication
│  └─ useEditMode
└─ Styles/
   ├─ globals.css (Tailwind imports)
   ├─ colors.css (TransKeep color palette)
   └─ spacing.css (Tailwind extensions)
```

### 9.2 Key Implementation Notes

**ReviewPanel (Hero Component):**
- Use pdf.js for rendering (lightweight, customizable)
- Implement scroll synchronization with JavaScript
- Hover highlighting requires mapping PDF coordinates to visual elements
- Consider performance: 500+ page PDFs need efficient rendering

**ToneSelector:**
- Radio button group for presets
- Textarea for custom input
- "Apply Tone" triggers API call to Claude Haiku
- State management: Current tone, previous tones (for undo)

**EditPanel:**
- Inline text editing with contentEditable or textarea
- Fetch alternatives from Claude API
- Preview changes in ReviewPanel in real-time
- Apply button updates translation state

### 9.3 Color & Typography in Tailwind

**Extend Tailwind config:**

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        'confidence': '#2563EB',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'highlight': '#DBEAFE',
      },
      fontSize: {
        'page-title': ['32px', '40px'],
        'section-title': ['24px', '32px'],
        'body': ['16px', '24px'],
        'small': ['14px', '20px'],
        'caption': ['12px', '16px'],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'base': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      boxShadow: {
        'hover': '0 2px 4px rgba(0,0,0,0.05)',
        'card': '0 1px 3px rgba(0,0,0,0.1)',
        'float': '0 10px 15px rgba(0,0,0,0.1)',
      },
    },
  },
};
```

### 9.4 Testing Checklist

**Visual Testing:**
- ✓ All screens render correctly at breakpoints
- ✓ Colors match spec (use color picker to verify)
- ✓ Spacing is consistent (24px base grid)
- ✓ Typography hierarchy is clear

**Interaction Testing:**
- ✓ Hover highlighting works on both PDF panels
- ✓ Tone preset selection updates immediately
- ✓ Edit panel appears and disappears smoothly
- ✓ Download button triggers file download

**Accessibility Testing:**
- ✓ Tab navigation works through all elements
- ✓ Focus indicator visible at all times
- ✓ Screen reader announces states and actions
- ✓ Keyboard shortcuts work as documented
- ✓ Color contrast meets WCAG AA (4.5:1)

---

## 10. Design Evolution for Phase 2

**What stays the same:**
- Core aesthetic (Figma-inspired, minimal)
- Side-by-side review (hero pattern)
- Confidence-driven emotional tone

**What evolves:**
- **Collaboration features** — Multi-user editing interface with presence indicators
- **Glossary management** — Term database UI, auto-apply visualization
- **Project management** — Document collections, version history, favorites
- **Mobile app** — Native apps with touch-optimized interfaces
- **Dark mode** — Option for users who prefer dark interface (Phase 2+)

---

## Appendix: Design Handoff for Development

### Assets Provided

1. **ux-design-specification.md** (this document)
2. **Tailwind configuration** (colors, typography, spacing)
3. **Component specifications** (shadcn/ui + custom)
4. **Interaction patterns** (behaviors, micro-interactions)
5. **Responsive breakpoints** (desktop, tablet, mobile)
6. **Accessibility checklist** (WCAG 2.1 AA compliance)

### Next Steps for Development

1. ✅ Frontend developers build components using shadcn/ui
2. ✅ Implement ReviewPanel with pdf.js
3. ✅ Connect UI to backend APIs
4. ✅ Test responsiveness at all breakpoints
5. ✅ Validate accessibility with screen readers
6. ✅ Iterate based on user feedback in beta

### Confidence Indicators (How to Know You're On Track)

- ✓ Side-by-side review is intuitive (users don't need explanation)
- ✓ Hover highlighting works smoothly (no lag, obvious pairing)
- ✓ Tone selection feels quick (presets obvious, applying is fast)
- ✓ Editing feels empowering (users try it, don't just download as-is)
- ✓ Overall interface feels "premium" (clean, spacious, polished)
- ✓ Users report high confidence in translations

---

**Status:** Ready for development  
**Created:** November 14, 2025  
**Track:** Enterprise Method - Greenfield  
**Next:** Architecture workflow will design the technical infrastructure

