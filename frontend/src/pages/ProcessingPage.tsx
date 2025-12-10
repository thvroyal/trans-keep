import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Loader2, CheckCircle2, XCircle, FileText, Clock, DollarSign } from 'lucide-react';
import { toast } from 'sonner';

interface StatusResponse {
  job_id: string;
  status: string;
  progress: number;
  file_name?: string;
  page_count?: number;
  total_blocks?: number;
  translated_blocks?: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  eta_seconds?: number;
  source_language?: string;
  target_language?: string;
  estimated_cost_usd?: number;
  error_message?: string;
}

export function ProcessingPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [isComplete, setIsComplete] = useState(false);

  // Poll for status every 2 seconds
  const { data: status, error, isLoading } = useQuery<StatusResponse>({
    queryKey: ['translationStatus', jobId],
    queryFn: async () => {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await fetch(`${apiUrl}/api/v1/status/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login');
          throw new Error('Session expired');
        }
        if (response.status === 404) {
          throw new Error('Translation job not found');
        }
        throw new Error('Failed to fetch status');
      }

      return response.json();
    },
    refetchInterval: (data) => {
      // Stop polling if completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return 2000; // Poll every 2 seconds
    },
    enabled: !!jobId && !isComplete,
  });

  // Handle completion
  useEffect(() => {
    if (status?.status === 'completed') {
      setIsComplete(true);
      toast.success('Translation completed!');
      // Navigate to review page after 2 seconds
      setTimeout(() => {
        navigate(`/review/${jobId}`);
      }, 2000);
    } else if (status?.status === 'failed') {
      setIsComplete(true);
      toast.error(status.error_message || 'Translation failed');
    }
  }, [status, jobId, navigate]);

  // Format ETA
  const formatETA = (seconds?: number): string => {
    if (!seconds) return 'Calculating...';
    if (seconds < 60) return `${seconds} seconds`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Get status display
  const getStatusDisplay = (statusValue: string) => {
    switch (statusValue) {
      case 'pending':
        return { text: 'Queued', icon: Clock, color: 'text-gray-500' };
      case 'extracting':
        return { text: 'Extracting Text', icon: FileText, color: 'text-blue-500' };
      case 'translating':
        return { text: 'Translating', icon: Loader2, color: 'text-purple-500' };
      case 'completed':
        return { text: 'Complete', icon: CheckCircle2, color: 'text-green-500' };
      case 'failed':
        return { text: 'Failed', icon: XCircle, color: 'text-red-500' };
      default:
        return { text: statusValue, icon: Loader2, color: 'text-gray-500' };
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12 p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-start gap-3">
            <XCircle className="h-6 w-6 text-red-500 mt-0.5" />
            <div>
              <h3 className="text-lg font-semibold text-red-900">Error Loading Status</h3>
              <p className="text-red-700 mt-1">{(error as Error).message}</p>
              <button
                onClick={() => navigate('/upload')}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Return to Upload
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!status) {
    return null;
  }

  const statusDisplay = getStatusDisplay(status.status);
  const StatusIcon = statusDisplay.icon;

  return (
    <div className="max-w-3xl mx-auto mt-12 p-8">
      <div className="bg-white rounded-lg shadow-lg p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className={`inline-flex items-center gap-2 ${statusDisplay.color} mb-4`}>
            <StatusIcon className={`h-8 w-8 ${status.status === 'translating' || status.status === 'extracting' ? 'animate-spin' : ''}`} />
          </div>
          <h1 className="text-3xl font-bold text-gray-900">{statusDisplay.text}</h1>
          {status.file_name && (
            <p className="text-gray-600 mt-2">{status.file_name}</p>
          )}
        </div>

        {/* Progress Bar */}
        {status.status !== 'failed' && (
          <div className="mb-8">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <span className="text-sm font-medium text-gray-900">{status.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full transition-all duration-300 ease-out"
                style={{ width: `${status.progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Status Details */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          {status.page_count && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Pages</div>
              <div className="text-xl font-semibold text-gray-900">{status.page_count}</div>
            </div>
          )}
          
          {status.total_blocks && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Text Blocks</div>
              <div className="text-xl font-semibold text-gray-900">
                {status.translated_blocks || 0} / {status.total_blocks}
              </div>
            </div>
          )}
          
          {status.eta_seconds !== null && status.eta_seconds !== undefined && status.status !== 'completed' && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Time Remaining
              </div>
              <div className="text-xl font-semibold text-gray-900">{formatETA(status.eta_seconds)}</div>
            </div>
          )}
          
          {status.estimated_cost_usd !== null && status.estimated_cost_usd !== undefined && (
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600 flex items-center gap-1">
                <DollarSign className="h-4 w-4" />
                Cost
              </div>
              <div className="text-xl font-semibold text-gray-900">
                ${status.estimated_cost_usd.toFixed(4)}
              </div>
            </div>
          )}
        </div>

        {/* Language Info */}
        {status.source_language && status.target_language && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="text-sm text-blue-900">
              Translating from <span className="font-semibold">{status.source_language}</span> to{' '}
              <span className="font-semibold">{status.target_language}</span>
            </div>
          </div>
        )}

        {/* Error Message */}
        {status.error_message && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-2">
              <XCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <div className="font-semibold text-red-900">Error</div>
                <div className="text-sm text-red-700 mt-1">{status.error_message}</div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-center gap-4">
          {status.status === 'completed' && (
            <button
              onClick={() => navigate(`/review/${jobId}`)}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
            >
              View Translation
            </button>
          )}
          {status.status === 'failed' && (
            <button
              onClick={() => navigate('/upload')}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              Try Again
            </button>
          )}
          {status.status !== 'completed' && status.status !== 'failed' && (
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-3 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 font-medium"
            >
              Go to Dashboard
            </button>
          )}
        </div>
      </div>

      {/* Job ID (for debugging) */}
      <div className="mt-6 text-center">
        <p className="text-xs text-gray-500">Job ID: {status.job_id}</p>
      </div>
    </div>
  );
}
