/**
 * Error message component with actionable guidance
 */

import { AlertCircle, HelpCircle, ExternalLink } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export interface ErrorMessageData {
  title: string
  message: string
  category: 'network' | 'api' | 'user' | 'server' | 'file'
  actionable_steps: string[]
  support_contact?: string
}

interface ErrorMessageProps {
  error: ErrorMessageData | string
  onRetry?: () => void
  onDismiss?: () => void
  showSupport?: boolean
}

export function ErrorMessage({ error, onRetry, onDismiss, showSupport = true }: ErrorMessageProps) {
  // Handle string errors
  const errorData: ErrorMessageData =
    typeof error === 'string'
      ? {
          title: 'An Error Occurred',
          message: error,
          category: 'server',
          actionable_steps: ['Try again', 'If the problem persists, contact support'],
        }
      : error

  const getCategoryColor = () => {
    switch (errorData.category) {
      case 'network':
        return 'border-blue-200 bg-blue-50 text-blue-900'
      case 'api':
        return 'border-yellow-200 bg-yellow-50 text-yellow-900'
      case 'user':
        return 'border-purple-200 bg-purple-50 text-purple-900'
      case 'file':
        return 'border-orange-200 bg-orange-50 text-orange-900'
      case 'server':
      default:
        return 'border-red-200 bg-red-50 text-red-900'
    }
  }

  const getCategoryIcon = () => {
    switch (errorData.category) {
      case 'network':
      case 'api':
      case 'server':
        return AlertCircle
      case 'user':
      case 'file':
      default:
        return HelpCircle
    }
  }

  const Icon = getCategoryIcon()
  const colorClass = getCategoryColor()

  return (
    <Card className={`${colorClass} border-2`}>
      <CardContent className="p-6">
        <div className="flex items-start gap-4">
          <Icon className="h-6 w-6 flex-shrink-0 mt-0.5" />
          <div className="flex-1 space-y-3">
            <div>
              <h3 className="font-semibold text-lg mb-1">{errorData.title}</h3>
              <p className="text-sm opacity-90">{errorData.message}</p>
            </div>

            {errorData.actionable_steps.length > 0 && (
              <div className="space-y-1">
                <p className="text-xs font-medium opacity-75">What you can do:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {errorData.actionable_steps.map((step, index) => (
                    <li key={index} className="opacity-90">
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex flex-wrap gap-2 pt-2">
              {onRetry && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  className="border-current text-current hover:bg-current hover:text-white"
                >
                  Try Again
                </Button>
              )}
              {showSupport && errorData.support_contact && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    window.location.href = `mailto:${errorData.support_contact}?subject=Support Request`
                  }}
                  className="gap-1"
                >
                  <ExternalLink className="h-3 w-3" />
                  Contact Support
                </Button>
              )}
              {onDismiss && (
                <Button size="sm" variant="ghost" onClick={onDismiss}>
                  Dismiss
                </Button>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

/**
 * Degraded mode indicator component
 */
interface DegradedModeProps {
  message: string
  onDismiss?: () => void
}

export function DegradedModeIndicator({ message, onDismiss }: DegradedModeProps) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <p className="text-sm text-yellow-900 font-medium">Degraded Mode</p>
          <p className="text-sm text-yellow-800 mt-1">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-yellow-600 hover:text-yellow-800 text-sm"
          >
            Dismiss
          </button>
        )}
      </div>
    </div>
  )
}
