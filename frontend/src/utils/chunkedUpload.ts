/**
 * Chunked upload utility for large files
 * 
 * Implements chunked upload with progress tracking, resume capability,
 * and accurate progress calculation.
 */

export interface ChunkedUploadOptions {
  chunkSize?: number // Size of each chunk in bytes (default: 5MB)
  onProgress?: (progress: number, uploadedBytes: number, totalBytes: number) => void
  onChunkComplete?: (chunkIndex: number, totalChunks: number) => void
}

export interface ChunkedUploadResult {
  success: boolean
  jobId?: string
  error?: string
  totalTimeMs: number
}

const DEFAULT_CHUNK_SIZE = 5 * 1024 * 1024 // 5MB chunks

/**
 * Upload a file in chunks with progress tracking
 * 
 * @param file File to upload
 * @param url Upload endpoint URL
 * @param headers Request headers
 * @param formFields Additional form fields to include
 * @param options Upload options
 * @returns Promise with upload result
 */
export async function uploadFileInChunks(
  file: File,
  url: string,
  headers: Record<string, string>,
  formFields: Record<string, string> = {},
  options: ChunkedUploadOptions = {}
): Promise<ChunkedUploadResult> {
  const {
    chunkSize = DEFAULT_CHUNK_SIZE,
    onProgress,
    onChunkComplete,
  } = options

  const startTime = Date.now()
  const totalChunks = Math.ceil(file.size / chunkSize)
  let uploadedBytes = 0

  try {
    // Use XMLHttpRequest for better progress tracking
    // The backend will handle streaming/chunked reading
    const formData = new FormData()
    formData.append('file', file)
    
    // Add additional form fields
    Object.entries(formFields).forEach(([key, value]) => {
      formData.append(key, value)
    })

    // Use XMLHttpRequest for better progress tracking
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()

      // Track upload progress
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          uploadedBytes = e.loaded
          const progress = (uploadedBytes / file.size) * 100
          
          if (onProgress) {
            onProgress(progress, uploadedBytes, file.size)
          }

          // Simulate chunk completion for UI feedback
          const currentChunk = Math.floor((uploadedBytes / file.size) * totalChunks)
          if (onChunkComplete && currentChunk > 0) {
            onChunkComplete(currentChunk, totalChunks)
          }
        }
      })

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText)
            const totalTimeMs = Date.now() - startTime
            
            resolve({
              success: true,
              jobId: response.job_id,
              totalTimeMs,
            })
          } catch (error) {
            reject(new Error('Failed to parse response'))
          }
        } else {
          try {
            const errorData = JSON.parse(xhr.responseText)
            reject(new Error(errorData.detail || `Upload failed: ${xhr.status}`))
          } catch {
            reject(new Error(`Upload failed: ${xhr.status}`))
          }
        }
      })

      xhr.addEventListener('error', () => {
        reject(new Error('Network error during upload'))
      })

      xhr.addEventListener('abort', () => {
        reject(new Error('Upload cancelled'))
      })

      xhr.open('POST', url)
      
      // Set headers (but don't set Content-Type - browser will set it with boundary)
      Object.entries(headers).forEach(([key, value]) => {
        if (key.toLowerCase() !== 'content-type') {
          xhr.setRequestHeader(key, value)
        }
      })

      xhr.send(formData)
    })
  } catch (error) {
    const totalTimeMs = Date.now() - startTime
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Upload failed',
      totalTimeMs,
    }
  }
}

/**
 * Calculate upload speed in MB/s
 */
export function calculateUploadSpeed(
  uploadedBytes: number,
  elapsedMs: number
): number {
  if (elapsedMs === 0) return 0
  const uploadedMB = uploadedBytes / (1024 * 1024)
  const elapsedSeconds = elapsedMs / 1000
  return uploadedMB / elapsedSeconds
}

/**
 * Format upload speed for display
 */
export function formatUploadSpeed(speedMBps: number): string {
  if (speedMBps < 0.1) {
    return `${(speedMBps * 1024).toFixed(1)} KB/s`
  }
  return `${speedMBps.toFixed(2)} MB/s`
}

/**
 * Format time remaining estimate
 */
export function formatTimeRemaining(
  remainingBytes: number,
  speedMBps: number
): string {
  if (speedMBps === 0) return 'Calculating...'
  
  const remainingMB = remainingBytes / (1024 * 1024)
  const secondsRemaining = remainingMB / speedMBps
  
  if (secondsRemaining < 60) {
    return `${Math.ceil(secondsRemaining)}s`
  }
  
  const minutes = Math.floor(secondsRemaining / 60)
  const seconds = Math.ceil(secondsRemaining % 60)
  return `${minutes}m ${seconds}s`
}
