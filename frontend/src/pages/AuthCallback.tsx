import { useEffect } from 'react'
import { useAuth } from '../hooks/useAuth'

export default function AuthCallback() {
  const { handleCallback } = useAuth()

  useEffect(() => {
    // Extract code from URL query parameters
    const urlParams = new URLSearchParams(window.location.search)
    const code = urlParams.get('code')
    const error = urlParams.get('error')

    if (error) {
      console.error('OAuth error:', error)
      // Redirect to home with error
      window.location.href = '/?error=oauth_failed'
      return
    }

    if (code) {
      handleCallback(code)
    } else {
      console.error('No authorization code in callback')
      window.location.href = '/?error=no_code'
    }
  }, [handleCallback])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center gap-4">
      <div className="w-10 h-10 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin"></div>
      <p className="text-lg">Completing sign in...</p>
    </div>
  )
}

