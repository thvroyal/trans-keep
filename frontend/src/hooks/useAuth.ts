import { useState, useEffect, useCallback } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface User {
  id: string
  email: string
  name: string | null
  picture_url: string | null
  subscription_tier: string
  created_at: string
}

interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  token: string | null
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
    token: null,
  })

  // Get token from httpOnly cookie or localStorage (fallback)
  const getToken = useCallback((): string | null => {
    // Try to get from cookie first (set by backend)
    const cookies = document.cookie.split(';')
    const tokenCookie = cookies.find((c) => c.trim().startsWith('access_token='))
    if (tokenCookie) {
      return tokenCookie.split('=')[1]
    }
    // Fallback to localStorage
    return localStorage.getItem('access_token')
  }, [])

  // Store token
  const setToken = useCallback((token: string) => {
    // Store in localStorage as fallback (httpOnly cookie is preferred but requires backend to set it)
    localStorage.setItem('access_token', token)
  }, [])

  // Remove token
  const removeToken = useCallback(() => {
    localStorage.removeItem('access_token')
    // Clear cookie if exists
    document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'
  }, [])

  // Check if token is expired or about to expire (within 5 minutes)
  const isTokenExpiring = useCallback((token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // Convert to milliseconds
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000
      return exp - now < fiveMinutes
    } catch {
      return true // If we can't parse, assume expired
    }
  }, [])

  // Refresh token by re-authenticating (for now, just redirect to sign in)
  // In production, you might have a refresh token endpoint
  const refreshToken = useCallback(async () => {
    // For JWT tokens, we can't refresh without re-authenticating
    // So we'll just clear the token and require re-login
    removeToken()
    setState((prev) => ({
      ...prev,
      user: null,
      isAuthenticated: false,
      isLoading: false,
      token: null,
    }))
    // Optionally redirect to sign in
    // window.location.href = '/'
  }, [removeToken])

  // Fetch user info with automatic token refresh
  const fetchUser = useCallback(async (token: string) => {
    try {
      // Check if token is expiring
      if (isTokenExpiring(token)) {
        console.warn('Token is expiring, attempting refresh...')
        await refreshToken()
        return
      }

      const response = await fetch(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const user = await response.json()
        setState((prev) => ({
          ...prev,
          user,
          isAuthenticated: true,
          isLoading: false,
          token,
        }))
      } else if (response.status === 401) {
        // Token expired or invalid, clear it
        console.warn('Token invalid, clearing...')
        removeToken()
        setState((prev) => ({
          ...prev,
          user: null,
          isAuthenticated: false,
          isLoading: false,
          token: null,
        }))
      } else {
        // Other error
        throw new Error(`Failed to fetch user: ${response.statusText}`)
      }
    } catch (error) {
      console.error('Failed to fetch user:', error)
      removeToken()
      setState((prev) => ({
        ...prev,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        token: null,
      }))
    }
  }, [removeToken, isTokenExpiring, refreshToken])

  // Check authentication on mount
  useEffect(() => {
    const token = getToken()
    if (token) {
      fetchUser(token)
    } else {
      setState((prev) => ({ ...prev, isLoading: false }))
    }
  }, [getToken, fetchUser])

  // Sign in with Google
  const signIn = useCallback(async () => {
    try {
      // Get OAuth URL from backend
      const response = await fetch(`${API_URL}/api/v1/auth/google`)
      const data = await response.json()
      
      // Redirect to Google OAuth
      window.location.href = data.auth_url
    } catch (error) {
      console.error('Failed to initiate OAuth:', error)
    }
  }, [])

  // Handle OAuth callback
  const handleCallback = useCallback(async (code: string) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/auth/google/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      })

      if (response.ok) {
        const data: TokenResponse = await response.json()
        setToken(data.access_token)
        await fetchUser(data.access_token)
        // Redirect to home
        window.location.href = '/'
      } else {
        console.error('OAuth callback failed')
      }
    } catch (error) {
      console.error('Failed to handle OAuth callback:', error)
    }
  }, [setToken, fetchUser])

  // Sign out
  const signOut = useCallback(async () => {
    try {
      await fetch(`${API_URL}/api/v1/auth/logout`, {
        method: 'POST',
      })
    } catch (error) {
      console.error('Failed to sign out:', error)
    } finally {
      removeToken()
      setState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        token: null,
      })
    }
  }, [removeToken])

  return {
    user: state.user,
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    token: state.token,
    signIn,
    signOut,
    handleCallback,
  }
}

