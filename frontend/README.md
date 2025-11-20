# TransKeep Frontend

React 18 + TypeScript + Vite application for the TransKeep document translation platform.

## 🎯 Quick Start

### Development

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Building for Production

```bash
npm run build
npm run preview
```

## 📦 Dependencies

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Lightning-fast bundler
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: High-quality React components
- **Zustand**: State management
- **TanStack Query**: Data fetching & caching
- **pdf.js**: PDF rendering
- **axios**: HTTP client

## 📁 Project Structure

```
src/
├── components/        # React components
│   ├── ReviewPanel.tsx       # Hero: dual PDF viewer
│   ├── ToneSelector.tsx      # Tone customization
│   ├── EditPanel.tsx         # Text editing
│   └── [shadcn/ui imports]
├── pages/            # Route pages
│   ├── Upload.tsx           # File upload
│   ├── Processing.tsx        # Status polling
│   ├── Review.tsx           # Side-by-side review
│   └── NotFound.tsx
├── hooks/            # Custom hooks
│   ├── useAuth.ts           # OAuth state
│   ├── useUpload.ts         # File upload logic
│   ├── useTranslation.ts    # Status polling
│   └── usePDFViewer.ts      # PDF rendering
├── services/         # API clients
│   └── api.ts               # Axios + endpoints
├── stores/           # Zustand stores
│   └── appStore.ts          # Global state
├── styles/           # Global styles
├── App.tsx           # Router setup
└── main.tsx          # Entry point
```

## 🛠 Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Linting (configure ESLint)
npm run lint

# Format code (configure Prettier)
npm run format

# Type checking
npm run type-check

# Run tests
npm run test
```

## 🎨 Styling

### Tailwind CSS

Configuration in `tailwind.config.ts`. TransKeep uses a custom color palette:

```typescript
colors: {
  primary: '#...',    // Main brand color
  secondary: '#...',  // Accent color
  success: '#...',
  warning: '#...',
  error: '#...',
}
```

### shadcn/ui Components

Add components with:

```bash
npx shadcn-ui@latest add [component-name]
```

Example components:
- `Button`
- `Card`
- `Dialog`
- `Dropdown Menu`
- `Input`
- `Progress`
- `Spinner`

## 🔄 State Management (Zustand)

Global app store in `src/stores/appStore.ts`:

```typescript
interface AppStore {
  user: User | null
  currentJob: TranslationJob | null
  settings: UserSettings
  
  setUser: (user: User) => void
  setCurrentJob: (job: TranslationJob) => void
  updateSettings: (settings: Partial<UserSettings>) => void
}
```

## 📡 API Integration

Axios client in `src/services/api.ts`:

```typescript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

// Endpoints
POST   /api/v1/upload         # Upload PDF
GET    /api/v1/status/{id}    # Poll status
GET    /api/v1/download/{id}  # Download result
```

## 🔐 Authentication

Google OAuth via backend `better-auth`:

```typescript
// useAuth hook
const { user, login, logout } = useAuth()
```

## 📊 Data Fetching

TanStack Query for caching and polling:

```typescript
// Status polling
const { data: status } = useQuery({
  queryKey: ['status', jobId],
  queryFn: () => getStatus(jobId),
  refetchInterval: 2000, // Poll every 2s
})
```

## 🧪 Testing

```bash
npm run test
npm run test:watch
npm run test:coverage
```

Use Vitest + React Testing Library.

## 🚀 Deployment

### Docker Build

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
CMD ["npm", "run", "preview"]
```

### CloudFront Distribution

- Origin: S3 bucket with built files
- Distribution: Global edge locations
- Caching: Long TTL for assets, short for index.html

## 🔧 Environment Variables

Create `.env.local`:

```
VITE_API_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your_client_id_here
```

See `.env.example` for all available variables.

## 📚 Resources

- [React Docs](https://react.dev)
- [Vite Docs](https://vitejs.dev)
- [Tailwind Docs](https://tailwindcss.com)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [TypeScript Docs](https://www.typescriptlang.org)

## 🐛 Troubleshooting

### Port 5173 already in use
```bash
# Kill process
lsof -i :5173
kill -9 <PID>

# Or use different port
npm run dev -- --port 3001
```

### Module not found errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
npm install
```

### Hot reload not working
```bash
# Check .env configuration
# Restart dev server
npm run dev
```

---

**Part of TransKeep MVP** | Last Updated: 2025-11-14

