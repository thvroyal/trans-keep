/**
 * Retry utility with exponential backoff
 * 
 * Implements retry logic with configurable attempts, backoff strategy,
 * and retry indicators for network operations.
 */

export interface RetryOptions {
  maxAttempts?: number
  initialBackoffMs?: number
  maxBackoffMs?: number
  onRetry?: (attempt: number, error: Error) => void
  shouldRetry?: (error: Error) => boolean
}

export interface RetryResult<T> {
  result: T
  attempts: number
  totalTimeMs: number
}

/**
 * Retry a function with exponential backoff
 * 
 * @param fn Function to retry (must return a Promise)
 * @param options Retry configuration
 * @returns Promise that resolves with the result or rejects after max attempts
 * 
 * @example
 * ```typescript
 * const result = await withRetry(
 *   () => fetch('/api/upload', { method: 'POST', body: formData }),
 *   {
 *     maxAttempts: 3,
 *     initialBackoffMs: 1000,
 *     onRetry: (attempt, error) => console.log(`Retry ${attempt}: ${error.message}`)
 *   }
 * )
 * ```
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const {
    maxAttempts = 3,
    initialBackoffMs = 1000,
    maxBackoffMs = 10000,
    onRetry,
    shouldRetry = () => true,
  } = options

  const startTime = Date.now()
  let lastError: Error | null = null

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await fn()
      const totalTimeMs = Date.now() - startTime
      
      return {
        result,
        attempts: attempt,
        totalTimeMs,
      }
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error))
      
      // Check if we should retry this error
      if (!shouldRetry(lastError)) {
        throw lastError
      }

      // Don't retry on last attempt
      if (attempt >= maxAttempts) {
        break
      }

      // Calculate exponential backoff: 1s, 2s, 4s (capped at maxBackoffMs)
      const backoffMs = Math.min(
        initialBackoffMs * Math.pow(2, attempt - 1),
        maxBackoffMs
      )

      // Notify about retry
      if (onRetry) {
        onRetry(attempt, lastError)
      }

      // Wait before retrying
      await new Promise((resolve) => setTimeout(resolve, backoffMs))
    }
  }

  // All attempts failed
  const totalTimeMs = Date.now() - startTime
  throw new RetryError(
    `Failed after ${maxAttempts} attempts`,
    lastError!,
    maxAttempts,
    totalTimeMs
  )
}

/**
 * Check if an error is a network error that should be retried
 */
export function isNetworkError(error: Error): boolean {
  const networkErrorMessages = [
    'network',
    'fetch',
    'timeout',
    'connection',
    'econnrefused',
    'enotfound',
    'econnreset',
  ]

  const message = error.message.toLowerCase()
  return networkErrorMessages.some((keyword) => message.includes(keyword))
}

/**
 * Check if an error is a timeout error
 */
export function isTimeoutError(error: Error): boolean {
  return (
    error.message.toLowerCase().includes('timeout') ||
    error.name === 'TimeoutError' ||
    error.name === 'AbortError'
  )
}

/**
 * Check if an error is a 5xx server error (from fetch Response)
 */
export function isServerError(response: Response): boolean {
  return response.status >= 500 && response.status < 600
}

/**
 * Custom error class for retry failures
 */
export class RetryError extends Error {
  constructor(
    message: string,
    public readonly originalError: Error,
    public readonly attempts: number,
    public readonly totalTimeMs: number
  ) {
    super(message)
    this.name = 'RetryError'
    // Maintain stack trace
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, RetryError)
    }
  }
}
