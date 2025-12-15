/**
 * API client with retry logic and error handling
 */

import { withRetry, isNetworkError, isRetryableHttpStatus, RetryError } from './retry'

export interface ApiError {
  message: string
  status?: number
  code?: string
  detail?: string
}

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
    public readonly code?: string,
    public readonly detail?: string
  ) {
    super(message)
    this.name = 'ApiClientError'
  }
}

/**
 * Get API base URL from environment
 */
function getApiUrl(): string {
  return import.meta.env.VITE_API_URL || 'http://localhost:8000'
}

/**
 * Get authentication token from storage
 */
function getAuthToken(): string | null {
  return localStorage.getItem('access_token')
}

/**
 * Fetch with automatic retry on network errors
 */
export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  retryOptions?: {
    maxAttempts?: number
    onRetry?: (attempt: number, error: unknown) => void
  }
): Promise<Response> {
  const { maxAttempts = 3, onRetry } = retryOptions || {}

  return withRetry(
    async () => {
      const response = await fetch(url, options)

      // Check if response status is retryable
      if (!response.ok && isRetryableHttpStatus(response.status)) {
        const errorData = await response.json().catch(() => ({
          detail: `HTTP ${response.status}: ${response.statusText}`,
        }))
        throw new ApiClientError(
          errorData.detail || response.statusText,
          response.status,
          'HTTP_ERROR',
          errorData.detail
        )
      }

      return response
    },
    {
      maxAttempts,
      retryable: (error) => {
        // Retry network errors and retryable HTTP status codes
        if (isNetworkError(error)) {
          return true
        }
        if (error instanceof ApiClientError && error.status) {
          return isRetryableHttpStatus(error.status)
        }
        return false
      },
      onRetry: (attempt, error) => {
        if (onRetry) {
          onRetry(attempt, error)
        }
      },
    }
  )
}

/**
 * Make authenticated API request with retry
 */
export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestInit = {},
  retryOptions?: {
    maxAttempts?: number
    onRetry?: (attempt: number, error: unknown) => void
  }
): Promise<T> {
  const apiUrl = getApiUrl()
  const token = getAuthToken()

  const headers: HeadersInit = {
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetchWithRetry(
    `${apiUrl}${endpoint}`,
    {
      ...options,
      headers,
    },
    retryOptions
  )

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      detail: `HTTP ${response.status}: ${response.statusText}`,
    }))

    throw new ApiClientError(
      errorData.detail || response.statusText,
      response.status,
      'API_ERROR',
      errorData.detail
    )
  }

  return response.json()
}

/**
 * Upload file with retry and progress tracking
 */
export async function uploadFile(
  endpoint: string,
  formData: FormData,
  options: {
    onProgress?: (progress: number) => void
    onRetry?: (attempt: number, error: unknown) => void
    maxAttempts?: number
  } = {}
): Promise<unknown> {
  const { onProgress, onRetry, maxAttempts = 3 } = options

  return withRetry(
    async () => {
      const apiUrl = getApiUrl()
      const token = getAuthToken()

      const xhr = new XMLHttpRequest()

      return new Promise((resolve, reject) => {
        xhr.upload.addEventListener('progress', (e) => {
          if (e.lengthComputable && onProgress) {
            const progress = (e.loaded / e.total) * 100
            onProgress(progress)
          }
        })

        xhr.addEventListener('load', () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            try {
              const response = JSON.parse(xhr.responseText)
              resolve(response)
            } catch {
              resolve(xhr.responseText)
            }
          } else {
            try {
              const errorData = JSON.parse(xhr.responseText)
              reject(
                new ApiClientError(
                  errorData.detail || `HTTP ${xhr.status}`,
                  xhr.status,
                  'UPLOAD_ERROR',
                  errorData.detail
                )
              )
            } catch {
              reject(
                new ApiClientError(
                  `HTTP ${xhr.status}: ${xhr.statusText}`,
                  xhr.status
                )
              )
            }
          }
        })

        xhr.addEventListener('error', () => {
          reject(new ApiClientError('Network error during upload'))
        })

        xhr.addEventListener('timeout', () => {
          reject(new ApiClientError('Upload timeout'))
        })

        xhr.open('POST', `${apiUrl}${endpoint}`)
        if (token) {
          xhr.setRequestHeader('Authorization', `Bearer ${token}`)
        }

        xhr.send(formData)
      })
    },
    {
      maxAttempts,
      retryable: (error) => {
        if (isNetworkError(error)) {
          return true
        }
        if (error instanceof ApiClientError && error.status) {
          return isRetryableHttpStatus(error.status)
        }
        return false
      },
      onRetry: (attempt, error) => {
        if (onRetry) {
          onRetry(attempt, error)
        }
      },
    }
  )
}
