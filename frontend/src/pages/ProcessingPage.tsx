import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { FileText, Check, Circle, Loader2 } from 'lucide-react'

interface JobStatus {
  job_id: string
  status: 'pending' | 'extracting' | 'translating' | 'applying_tone' | 'reconstructing' | 'completed' | 'failed'
  progress: number
  current_page?: number
  total_pages?: number
  filename?: string
  source_language?: string
  target_language?: string
  error?: string
}

const PROCESSING_STEPS = [
  { key: 'extracting', label: 'Extracting text' },
  { key: 'translating', label: 'Translating...' },
  { key: 'applying_tone', label: 'Applying tone' },
  { key: 'reconstructing', label: 'Reconstructing PDF' },
]

export default function ProcessingPage() {
  const { jobId } = useParams<{ jobId: string }>()
  const navigate = useNavigate()
  const [status, setStatus] = useState<JobStatus | null>(null)
  const [estimatedTime, setEstimatedTime] = useState<number>(60)

  useEffect(() => {
    if (!jobId) return

    const pollStatus = async () => {
      try {
        const token = localStorage.getItem('access_token')
        const response = await fetch(`/api/v1/status/${jobId}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })

        if (response.ok) {
          const data: JobStatus = await response.json()
          setStatus(data)

          if (data.total_pages) {
            const remainingPages = data.total_pages - (data.current_page || 0)
            setEstimatedTime(Math.max(5, remainingPages * 1))
          }

          if (data.status === 'completed') {
            navigate(`/review/${jobId}`)
          } else if (data.status === 'failed') {
            console.error('Job failed:', data.error)
          }
        }
      } catch (error) {
        console.error('Failed to fetch status:', error)
      }
    }

    pollStatus()
    const interval = setInterval(pollStatus, 2000)

    return () => clearInterval(interval)
  }, [jobId, navigate])

  const getStepStatus = (stepKey: string) => {
    if (!status) return 'pending'

    const stepOrder = PROCESSING_STEPS.map((s) => s.key)
    const currentIndex = stepOrder.indexOf(status.status)
    const stepIndex = stepOrder.indexOf(stepKey)

    if (currentIndex === -1) return 'pending'
    if (stepIndex < currentIndex) return 'completed'
    if (stepIndex === currentIndex) return 'current'
    return 'pending'
  }

  return (
    <div className="container max-w-lg mx-auto px-4 py-16">
      <Card className="bg-card shadow-md">
        <CardContent className="p-8">
          <div className="flex items-center gap-3 mb-6">
            <FileText className="w-8 h-8 text-primary" />
            <div>
              <p className="font-medium text-foreground">
                {status?.filename || 'document.pdf'}
              </p>
              <p className="text-sm text-muted-foreground">
                {status?.source_language || 'English'} → {status?.target_language || 'Japanese'}
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-medium text-foreground">{status?.progress || 0}%</span>
              </div>
              <Progress value={status?.progress || 0} className="h-2" />
            </div>

            {status?.current_page && status?.total_pages && (
              <p className="text-sm text-center text-muted-foreground">
                Page {status.current_page} of {status.total_pages}
              </p>
            )}

            <p className="text-sm text-center text-muted-foreground">
              ~{estimatedTime} seconds remaining
            </p>

            <div className="mt-8 space-y-3">
              {PROCESSING_STEPS.map((step) => {
                const stepStatus = getStepStatus(step.key)
                return (
                  <div key={step.key} className="flex items-center gap-3">
                    {stepStatus === 'completed' ? (
                      <Check className="w-5 h-5 text-success" />
                    ) : stepStatus === 'current' ? (
                      <Loader2 className="w-5 h-5 text-primary animate-spin" />
                    ) : (
                      <Circle className="w-5 h-5 text-muted" />
                    )}
                    <span
                      className={
                        stepStatus === 'completed'
                          ? 'text-muted-foreground'
                          : stepStatus === 'current'
                            ? 'text-foreground font-medium'
                            : 'text-muted-foreground'
                      }
                    >
                      {step.label}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
