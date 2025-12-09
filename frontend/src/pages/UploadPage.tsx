import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Upload, FileText, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'
import SignIn from '@/components/SignIn'

// Constants
const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB in bytes

const SUPPORTED_LANGUAGES = [
  { code: 'JA', name: 'Japanese' },
  { code: 'ZH', name: 'Chinese (Simplified)' },
  { code: 'DE', name: 'German' },
  { code: 'FR', name: 'French' },
  { code: 'ES', name: 'Spanish' },
  { code: 'KO', name: 'Korean' },
  { code: 'IT', name: 'Italian' },
  { code: 'PT-BR', name: 'Portuguese (Brazil)' },
]

export default function UploadPage() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [targetLanguage, setTargetLanguage] = useState('JA')
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const validateFile = useCallback((file: File): boolean => {
    // Check file type
    if (file.type !== 'application/pdf') {
      setError('Invalid file type. Only PDF files are supported.')
      toast.error('Invalid file type', {
        description: 'Please upload a PDF file.',
      })
      return false
    }

    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      const sizeMB = (file.size / 1024 / 1024).toFixed(2)
      setError(`File too large (${sizeMB} MB). Maximum size is 100 MB.`)
      toast.error('File too large', {
        description: `Your file is ${sizeMB} MB. Maximum size is 100 MB.`,
      })
      return false
    }

    // Check if file is empty
    if (file.size === 0) {
      setError('File is empty.')
      toast.error('Empty file', {
        description: 'Please upload a valid PDF file.',
      })
      return false
    }

    setError(null)
    return true
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile && validateFile(droppedFile)) {
        setFile(droppedFile)
        toast.success('File selected', {
          description: `${droppedFile.name} is ready to upload.`,
        })
      }
    },
    [validateFile]
  )

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0]
      if (selectedFile && validateFile(selectedFile)) {
        setFile(selectedFile)
        toast.success('File selected', {
          description: `${selectedFile.name} is ready to upload.`,
        })
      }
      // Reset input value to allow selecting the same file again
      e.target.value = ''
    },
    [validateFile]
  )

  const handleUpload = async () => {
    if (!file || !isAuthenticated) return

    // Validate file one more time before upload
    if (!validateFile(file)) {
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('target_language', targetLanguage.toLowerCase())
      formData.append('source_language', 'auto')

      const token = localStorage.getItem('access_token')
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

      const response = await fetch(`${apiUrl}/api/v1/upload`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        toast.success('Upload successful!', {
          description: 'Your document is being processed.',
        })
        navigate(`/processing/${data.job_id}`)
      } else {
        const errorData = await response.json().catch(() => ({
          detail: 'Upload failed. Please try again.',
        }))
        const errorMessage = errorData.detail || 'Upload failed. Please try again.'
        setError(errorMessage)
        toast.error('Upload failed', {
          description: errorMessage,
        })
      }
    } catch (error) {
      console.error('Upload failed:', error)
      const errorMessage = 'Network error. Please check your connection and try again.'
      setError(errorMessage)
      toast.error('Upload failed', {
        description: errorMessage,
      })
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="container max-w-2xl mx-auto px-4 py-16">
      <div className="text-center mb-12">
        <h1 className="text-h1 font-bold text-foreground mb-4">
          Translate Your Documents
        </h1>
        <p className="text-body text-muted-foreground">
          Upload a PDF and get a professionally translated document with format preservation
        </p>
      </div>

      <Card className="bg-card shadow-md">
        <CardContent className="p-8">
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-12
              flex flex-col items-center justify-center gap-4
              transition-colors duration-fast
              ${isDragging ? 'border-primary bg-accent' : 'border-border hover:border-primary/50'}
              ${file ? 'border-primary bg-accent/50' : ''}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />

            {file ? (
              <>
                <FileText className="w-12 h-12 text-primary" />
                <div className="text-center">
                  <p className="font-medium text-foreground">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.preventDefault()
                    setFile(null)
                  }}
                >
                  Remove
                </Button>
              </>
            ) : (
              <>
                <Upload className="w-12 h-12 text-muted-foreground" />
                <div className="text-center">
                  <p className="font-medium text-foreground">Drop your PDF here</p>
                  <p className="text-sm text-muted-foreground">or click to browse</p>
                </div>
                <p className="text-xs text-muted-foreground">Supports up to 100MB</p>
              </>
            )}
          </div>

          {error && (
            <div className="mt-4 p-3 bg-destructive-light rounded-md flex items-start gap-2">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          <div className="mt-6 space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground">
                Translate to:
              </label>
              <Select value={targetLanguage} onValueChange={setTargetLanguage}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  {SUPPORTED_LANGUAGES.map((lang) => (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {isAuthenticated ? (
              <Button
                className="w-full"
                size="lg"
                disabled={!file || isUploading}
                onClick={handleUpload}
              >
                {isUploading ? 'Uploading...' : 'Start Translation'}
              </Button>
            ) : (
              <div className="space-y-4">
                <p className="text-sm text-center text-muted-foreground">
                  Sign in to start translating
                </p>
                <SignIn />
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {isAuthenticated && (
        <p className="text-center text-sm text-muted-foreground mt-6">
          2 of 2 free translations remaining
        </p>
      )}
    </div>
  )
}
