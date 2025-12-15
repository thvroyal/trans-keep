/**
 * Tests for retry utility
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { withRetry, isNetworkError, isTimeoutError, RetryError } from '../retry'

describe('retry utility', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('withRetry', () => {
    it('should succeed on first attempt', async () => {
      const fn = vi.fn().mockResolvedValue('success')
      
      const result = await withRetry(fn, { maxAttempts: 3 })
      
      expect(result.result).toBe('success')
      expect(result.attempts).toBe(1)
      expect(fn).toHaveBeenCalledTimes(1)
    })

    it('should retry on network error', async () => {
      const fn = vi.fn()
        .mockRejectedValueOnce(new Error('network error'))
        .mockResolvedValue('success')
      
      const onRetry = vi.fn()
      
      const promise = withRetry(fn, {
        maxAttempts: 3,
        initialBackoffMs: 100,
        onRetry,
      })
      
      // Fast-forward timers
      await vi.runAllTimersAsync()
      
      const result = await promise
      
      expect(result.result).toBe('success')
      expect(result.attempts).toBe(2)
      expect(fn).toHaveBeenCalledTimes(2)
      expect(onRetry).toHaveBeenCalledTimes(1)
    })

    it('should give up after max attempts', async () => {
      const fn = vi.fn().mockRejectedValue(new Error('network error'))
      
      const promise = withRetry(fn, {
        maxAttempts: 3,
        initialBackoffMs: 100,
        shouldRetry: () => true,
      })
      
      await vi.runAllTimersAsync()
      
      await expect(promise).rejects.toThrow(RetryError)
      expect(fn).toHaveBeenCalledTimes(3)
    })

    it('should not retry if shouldRetry returns false', async () => {
      const fn = vi.fn().mockRejectedValue(new Error('permanent error'))
      
      const promise = withRetry(fn, {
        maxAttempts: 3,
        shouldRetry: () => false,
      })
      
      await expect(promise).rejects.toThrow('permanent error')
      expect(fn).toHaveBeenCalledTimes(1)
    })
  })

  describe('isNetworkError', () => {
    it('should detect network errors', () => {
      expect(isNetworkError(new Error('network timeout'))).toBe(true)
      expect(isNetworkError(new Error('connection failed'))).toBe(true)
      expect(isNetworkError(new Error('fetch error'))).toBe(true)
    })

    it('should not detect non-network errors', () => {
      expect(isNetworkError(new Error('validation error'))).toBe(false)
      expect(isNetworkError(new Error('permission denied'))).toBe(false)
    })
  })

  describe('isTimeoutError', () => {
    it('should detect timeout errors', () => {
      expect(isTimeoutError(new Error('timeout occurred'))).toBe(true)
      const timeoutError = new Error('timeout')
      timeoutError.name = 'TimeoutError'
      expect(isTimeoutError(timeoutError)).toBe(true)
    })
  })
})
