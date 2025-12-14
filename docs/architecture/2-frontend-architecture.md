# 2. Frontend Architecture

## 2.1 Frontend Stack & Rationale

| Layer | Technology | Why |
|-------|------------|-----|
| **Framework** | React 18 + TypeScript | Industry standard, great ecosystem, type safety |
| **Bundler** | Vite | Fast, modern, HMR for development |
| **Styling** | Tailwind CSS v4 | Utility-first, modern, efficient, Vite plugin integration |
| **Code Quality** | ESLint + Prettier | Consistent code style, catch errors early |
| **State** | Zustand | Lightweight, simple alternative to Redux |
| **Data Fetching** | TanStack Query | Caching, deduplication, polling (critical for status) |
| **Package Manager** | npm | Standard, reliable dependency management |
| **Router** | React Router v6 | Standard for SPA routing |
| **PDF Rendering** | pdf.js | Lightweight, browser-native PDF viewer |
| **Auth** | Google OAuth (via FastAPI) | Simple, secure, no password management |

## 2.2 Frontend Project Structure

```
frontend/
├─ src/
│  ├─ components/
│  │  ├─ SignIn.tsx (Google OAuth sign-in button)
│  │  ├─ ReviewPanel.tsx (hero component - dual PDF viewer)
│  │  ├─ ToneSelector.tsx (tone presets + custom input)
│  │  ├─ EditPanel.tsx (inline text editor)
│  │  └─ ProgressIndicator.tsx (step-by-step progress)
│  ├─ pages/
│  │  ├─ AuthCallback.tsx (OAuth callback handler)
│  │  ├─ Upload.tsx
│  │  ├─ Processing.tsx
│  │  ├─ Review.tsx (HERO PAGE)
│  │  └─ NotFound.tsx
│  ├─ hooks/
│  │  ├─ useAuth.ts (Google OAuth state, token management)
│  │  ├─ useUpload.ts (file upload logic)
│  │  ├─ useTranslation.ts (polling status)
│  │  └─ usePDFViewer.ts (PDF rendering)
│  ├─ services/
│  │  └─ api.ts (fetch client, endpoints)
│  ├─ stores/
│  │  └─ appStore.ts (Zustand: user, currentJob, settings)
│  ├─ index.css (Tailwind CSS v4 import: @import "tailwindcss")
│  ├─ App.tsx (Router setup, auth flow)
│  └─ main.tsx (Entry point)
├─ public/
│  └─ index.html
├─ .eslintrc.cjs (ESLint configuration)
├─ .prettierrc (Prettier configuration)
├─ vite.config.ts (Vite + Tailwind CSS v4 plugin)
├─ tsconfig.json
├─ package.json
└─ .env.local (API_URL=http://localhost:8000)
```

## 2.3 Frontend Development Setup

**Tailwind CSS v4 Configuration:**
- Uses `@tailwindcss/vite` plugin for seamless Vite integration
- Single CSS import: `@import "tailwindcss"` in `src/index.css`
- No PostCSS configuration required
- No `tailwind.config.ts` needed (uses CSS-first configuration)
- All styling via utility classes (no native CSS files)

**Code Quality Tools:**
- **ESLint**: TypeScript + React linting with recommended rules
- **Prettier**: Code formatting with ESLint integration
- **Scripts**: `npm run lint`, `npm run lint:fix`, `npm run format`, `npm run format:check`

**Styling Approach:**
- Utility-first CSS with Tailwind CSS v4
- No component-level CSS files
- Consistent design system via Tailwind utilities
- Responsive design using Tailwind breakpoints

## 2.4 Key Frontend Components

**ReviewPanel (Hero Component):**
- Dual PDF viewers using pdf.js
- Synchronized scrolling (default ON, toggle OFF)
- Hover highlighting (block-level mapping)
- Responsive: Desktop (2-col) → Tablet (2-col) → Mobile (tabs)

**StatusPolling (TanStack Query):**
```typescript
// Poll job status every 2 seconds while processing
useQuery({
  queryKey: ['translation', jobId],
  queryFn: () => api.getStatus(jobId),
  refetchInterval: 2000,
  enabled: status !== 'complete',
})
```

**Authentication Flow (Google OAuth + JWT):**

**Installation:**
```bash
# Backend (dependencies already in pyproject.toml)
# google-auth, python-jose, httpx

# Frontend
# No additional auth library needed - custom implementation
```

**Backend Setup:**
```python
# backend/app/routers/auth.py
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt

@router.get("/api/v1/auth/google")
async def initiate_google_oauth():
    # Returns Google OAuth URL for frontend redirect
    
@router.post("/api/v1/auth/google/callback")
async def google_oauth_callback(callback: GoogleOAuthCallback):
    # Exchanges OAuth code for ID token
    # Verifies ID token with Google
    # Creates/updates user in database
    # Returns JWT access token

@router.get("/api/v1/auth/me")
async def get_current_user_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    # Returns current user info from JWT token
```

**Frontend Flow:**
- User clicks "Sign in with Google" button
- Frontend calls `/api/v1/auth/google` to get OAuth URL
- Browser redirects to Google consent screen
- Google redirects to `/auth/callback` with auth code
- Frontend exchanges code via `/api/v1/auth/google/callback`
- Backend returns JWT token
- Frontend stores token in localStorage (httpOnly cookie enhancement possible)
- All API requests include `Authorization: Bearer <token>` header
- Token expiration detected and handled gracefully

**Implementation Details:**
- Custom `useAuth` hook manages authentication state
- Token persistence across page reloads
- Automatic token expiration detection (5-minute threshold)
- Graceful handling of expired/invalid tokens

## 2.4 State Management (Zustand)

```typescript
interface AppStore {
  // Auth
  user: {id, email, name, subscription} | null
  isAuthenticated: boolean
  login: (googleToken) => void
  logout: () => void

  // Current translation
  currentJob: {id, status, progress, file} | null
  setCurrentJob: (job) => void

  // UI
  reviewPanelSync: boolean
  toggleSync: () => void
  selectedBlock: {id, text} | null
  editMode: boolean
}
```

---
