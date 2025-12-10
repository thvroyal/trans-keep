import React from 'react'
import ReactDOM from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { router } from './router'
import { initTelemetry } from './otelConfig'
import './index.css'

// Create QueryClient for TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

// Initialize OpenTelemetry BEFORE rendering the app
// This must be done first to capture all traces
try {
  // Determine collector URL based on environment
  const collectorUrl =
    import.meta.env.VITE_OTEL_COLLECTOR_URL ||
    'http://localhost:4318/v1/traces'

  initTelemetry('transkeep-frontend', collectorUrl)
} catch (error) {
  console.error('Failed to initialize OpenTelemetry:', error)
  // Continue even if Otel initialization fails - don't break the app
}

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
)
