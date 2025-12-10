import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Download, Link2, Link2Off, Loader2, ArrowLeft } from 'lucide-react';
import { PDFViewer } from '@/components/PDFViewer';
import { useReviewStore } from '@/stores/reviewStore';
import { toast } from 'sonner';

export default function ReviewPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  
  // Review store state
  const { 
    syncScrolling, 
    setSyncScrolling,
    scrollPosition,
    setScrollPosition 
  } = useReviewStore();

  // Local state
  const [originalPdfUrl, setOriginalPdfUrl] = useState<string | null>(null);
  const [translatedPdfUrl, setTranslatedPdfUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('document.pdf');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load PDF URLs
  useEffect(() => {
    const loadPDFs = async () => {
      try {
        setIsLoading(true);
        const token = localStorage.getItem('access_token');
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        if (!token) {
          navigate('/login');
          return;
        }

        // Fetch translation details
        const response = await fetch(`${apiUrl}/api/v1/translation/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('Translation not found');
          }
          throw new Error('Failed to load translation');
        }

        const data = await response.json();
        
        // Set PDF URLs (these will be S3 presigned URLs from the backend)
        setOriginalPdfUrl(data.original_pdf_url);
        setTranslatedPdfUrl(data.translated_pdf_url);
        setFileName(data.file_name);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading PDFs:', err);
        setError((err as Error).message);
        setIsLoading(false);
      }
    };

    if (jobId) {
      loadPDFs();
    }
  }, [jobId, navigate]);

  // Handle scroll synchronization
  const handleScrollLeft = (scrollTop: number) => {
    if (syncScrolling) {
      setScrollPosition(scrollTop);
    }
  };

  const handleScrollRight = (scrollTop: number) => {
    if (syncScrolling) {
      setScrollPosition(scrollTop);
    }
  };

  // Toggle scroll sync
  const toggleSync = () => {
    setSyncScrolling(!syncScrolling);
    toast.success(syncScrolling ? 'Scroll sync disabled' : 'Scroll sync enabled');
  };

  // Download translated PDF
  const handleDownload = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/api/v1/download/${jobId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        // Open download URL in new tab
        window.open(data.download_url, '_blank');
        toast.success('Download started');
      } else {
        toast.error('Download failed');
      }
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Download failed');
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-4" />
          <p className="text-gray-600">Loading translation...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-12 p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
          <p className="text-red-700 mb-4">{error}</p>
          <Button
            onClick={() => navigate('/upload')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Upload
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Header Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-white shadow-sm">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/upload')}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="hidden md:inline">Back</span>
          </Button>
          <div className="h-6 w-px bg-gray-300" />
          <span className="text-sm font-medium text-gray-900">{fileName}</span>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={toggleSync}
            className="gap-2"
          >
            {syncScrolling ? (
              <>
                <Link2 className="h-4 w-4" />
                <span className="hidden md:inline">Synced</span>
              </>
            ) : (
              <>
                <Link2Off className="h-4 w-4" />
                <span className="hidden md:inline">Not Synced</span>
              </>
            )}
          </Button>

          <Button onClick={handleDownload} size="sm" className="gap-2">
            <Download className="h-4 w-4" />
            <span className="hidden md:inline">Download</span>
          </Button>
        </div>
      </div>

      {/* Side-by-Side PDF Viewers */}
      <div className="flex-1 grid grid-cols-1 md:grid-cols-2 overflow-hidden">
        {/* Original PDF */}
        <div className="flex flex-col border-r">
          <div className="px-4 py-2 bg-gray-50 border-b">
            <span className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              Original
            </span>
          </div>
          {originalPdfUrl ? (
            <PDFViewer
              pdfUrl={originalPdfUrl}
              onScroll={handleScrollLeft}
              syncedScrollPosition={syncScrolling ? scrollPosition : undefined}
              className="flex-1"
            />
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-100">
              <p className="text-gray-500">Original PDF not available</p>
            </div>
          )}
        </div>

        {/* Translated PDF */}
        <div className="flex flex-col">
          <div className="px-4 py-2 bg-blue-50 border-b">
            <span className="text-sm font-semibold text-blue-700 uppercase tracking-wide">
              Translated
            </span>
          </div>
          {translatedPdfUrl ? (
            <PDFViewer
              pdfUrl={translatedPdfUrl}
              onScroll={handleScrollRight}
              syncedScrollPosition={syncScrolling ? scrollPosition : undefined}
              className="flex-1"
            />
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-100">
              <p className="text-gray-500">Translated PDF not available yet</p>
              <p className="text-sm text-gray-400 mt-2">Translation may still be in progress</p>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Action Bar (Optional - for future tone customization) */}
      <div className="border-t bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center justify-center gap-4">
          <span className="text-sm text-gray-600">
            Review your translation above. Download when ready.
          </span>
        </div>
      </div>
    </div>
  );
}
