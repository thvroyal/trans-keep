import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Download, Link2, Link2Off, Loader2, ArrowLeft, FileText, X } from 'lucide-react';
import { PDFViewer } from '@/components/PDFViewer';
import { ToneSelector } from '@/components/ToneSelector';
import type { TonePreset } from '@/components/ToneSelector';
import { ToneComparison } from '@/components/ToneComparison';
import { BlocksPanel, type Block } from '@/components/BlocksPanel';
import { useReviewStore } from '@/stores/reviewStore';
import { useEditStore } from '@/store/editSlice';
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

  // Edit store state
  const { edits } = useEditStore();

  // Local state
  const [originalPdfUrl, setOriginalPdfUrl] = useState<string | null>(null);
  const [translatedPdfUrl, setTranslatedPdfUrl] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('document.pdf');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Tone customization state
  const [selectedTone, setSelectedTone] = useState<TonePreset | string>('professional');
  const [showToneSelector, setShowToneSelector] = useState(false);
  const [isApplyingTone, setIsApplyingTone] = useState(false);
  const [toneComparison, setToneComparison] = useState<{
    original: string;
    customized: string;
    tone: string;
    cost?: number;
  } | null>(null);

  // Blocks and editing state
  const [blocks, setBlocks] = useState<Block[]>([]);
  const [showBlocksPanel, setShowBlocksPanel] = useState(false);
  const [targetLanguage, setTargetLanguage] = useState<string>('JA');
  const [isLoadingBlocks, setIsLoadingBlocks] = useState(false);

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
        setTargetLanguage(data.target_language || 'JA');
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
      
      // Collect edits from store and format for API
      const editsArray = Array.from(edits.entries()).map(([blockId, edit]) => ({
        block_id: parseInt(blockId, 10), // Convert string to number
        text: edit.editedText,
      }));

      toast.info(`Preparing download${editsArray.length > 0 ? ` with ${editsArray.length} edit${editsArray.length > 1 ? 's' : ''}` : ''}...`);
      
      const response = await fetch(`${apiUrl}/api/v1/download/${jobId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          edits: editsArray,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        // Open download URL in new tab
        window.open(data.download_url, '_blank');
        toast.success('Download started');
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Download failed' }));
        toast.error(errorData.detail || 'Download failed');
      }
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Download failed');
    }
  };

  // Poll for tone completion
  const pollToneCompletion = async (maxAttempts = 30) => {
    const token = localStorage.getItem('access_token');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        // Check translation status
        const statusResponse = await fetch(`${apiUrl}/api/v1/translation/${jobId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          // If status is not applying_tone, check for comparison data
          if (statusData.status !== 'applying_tone') {
            // Try to load comparison data
            const comparisonResponse = await fetch(
              `${apiUrl}/api/v1/translation/${jobId}/tone/comparison`,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                },
              }
            );
            
            if (comparisonResponse.ok) {
              const comparisonData = await comparisonResponse.json();
              
              // Show first block for comparison
              if (comparisonData.blocks && comparisonData.blocks.length > 0) {
                const firstBlock = comparisonData.blocks[0];
                setToneComparison({
                  original: firstBlock.original,
                  customized: firstBlock.customized,
                  tone: comparisonData.tone,
                  cost: comparisonData.cost_usd,
                });
                setIsApplyingTone(false);
                setShowToneSelector(false);
                toast.success('Tone customization complete!');
                return;
              }
            }
          }
        }
        
        // Wait before next attempt
        await new Promise(resolve => setTimeout(resolve, 2000));
      } catch (error) {
        console.error('Error polling tone status:', error);
        // Continue polling
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Max attempts reached
    setIsApplyingTone(false);
    toast.warning('Tone customization is taking longer than expected. Please refresh the page.');
  };

  // Apply tone customization
  const handleApplyTone = async () => {
    if (!jobId) return;
    
    try {
      setIsApplyingTone(true);
      const token = localStorage.getItem('access_token');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      // Get cost estimate first
      const estimateResponse = await fetch(
        `${apiUrl}/api/v1/translation/${jobId}/tone/estimate?tone=${encodeURIComponent(selectedTone)}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      
      let estimatedCost: number | undefined;
      if (estimateResponse.ok) {
        const estimateData = await estimateResponse.json();
        estimatedCost = estimateData.estimated_cost_usd;
        if (estimatedCost) {
          toast.info(`Estimated cost: $${estimatedCost.toFixed(4)}`);
        }
      }
      
      // Apply tone
      const response = await fetch(`${apiUrl}/api/v1/translation/${jobId}/tone`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tone: selectedTone }),
      });

      if (response.ok) {
        toast.success('Tone customization started. Processing...');
        
        // Start polling for completion
        pollToneCompletion();
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to apply tone' }));
        toast.error(errorData.detail || 'Failed to apply tone');
        setIsApplyingTone(false);
      }
    } catch (error) {
      console.error('Tone application failed:', error);
      toast.error('Failed to apply tone');
      setIsApplyingTone(false);
    }
  };

  // Load existing tone comparison on mount
  useEffect(() => {
    const loadToneComparison = async () => {
      if (!jobId) return;
      
      try {
        const token = localStorage.getItem('access_token');
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        
        const response = await fetch(
          `${apiUrl}/api/v1/translation/${jobId}/tone/comparison`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );
        
        if (response.ok) {
          const data = await response.json();
          if (data.blocks && data.blocks.length > 0) {
            const firstBlock = data.blocks[0];
            setToneComparison({
              original: firstBlock.original,
              customized: firstBlock.customized,
              tone: data.tone,
              cost: data.cost_usd,
            });
          }
        }
      } catch (error) {
        // Silently fail - tone may not be applied yet
        console.debug('No tone comparison available:', error);
      }
    };
    
    if (jobId && !isLoading) {
      loadToneComparison();
    }
  }, [jobId, isLoading]);

  // Handle tone acceptance/rejection
  const handleAcceptTone = () => {
    toast.success('Tone customization accepted');
    setToneComparison(null);
    // Note: PDF reconstruction will use tone-customized text automatically
    // when status is RECONSTRUCTING or COMPLETED
  };

  const handleRejectTone = () => {
    toast.info('Keeping original translation');
    setToneComparison(null);
    // Note: User can still download original translation
  };

  // Load blocks for editing
  const loadBlocks = async () => {
    if (!jobId) return;
    
    try {
      setIsLoadingBlocks(true);
      const token = localStorage.getItem('access_token');
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/api/v1/translation/${jobId}/blocks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setBlocks(data.blocks || []);
        if (data.target_language) {
          setTargetLanguage(data.target_language);
        }
      } else {
        toast.error('Failed to load blocks');
      }
    } catch (error) {
      console.error('Error loading blocks:', error);
      toast.error('Failed to load blocks');
    } finally {
      setIsLoadingBlocks(false);
    }
  };

  // Get alternatives for a text
  const handleGetAlternatives = async (text: string): Promise<string[]> => {
    const token = localStorage.getItem('access_token');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${apiUrl}/api/v1/alternatives`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          target_lang: targetLanguage,
          count: 3,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data.alternatives || [];
      } else {
        throw new Error('Failed to get alternatives');
      }
    } catch (error) {
      console.error('Error getting alternatives:', error);
      throw error;
    }
  };

  // Re-translate text with tone
  const handleRetranslate = async (text: string, tone: string): Promise<string> => {
    const token = localStorage.getItem('access_token');
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    try {
      const response = await fetch(`${apiUrl}/api/v1/retranslate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          tone,
          target_lang: targetLanguage,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        return data.translated_text;
      } else {
        throw new Error('Failed to re-translate');
      }
    } catch (error) {
      console.error('Error re-translating:', error);
      throw error;
    }
  };

  // Load blocks when blocks panel is opened
  useEffect(() => {
    if (showBlocksPanel && blocks.length === 0 && !isLoadingBlocks) {
      loadBlocks();
    }
  }, [showBlocksPanel]);

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
            onClick={() => {
              setShowBlocksPanel(!showBlocksPanel);
              if (!showBlocksPanel && blocks.length === 0) {
                loadBlocks();
              }
            }}
            className="gap-2"
          >
            {showBlocksPanel ? (
              <>
                <X className="h-4 w-4" />
                <span className="hidden md:inline">Hide Blocks</span>
              </>
            ) : (
              <>
                <FileText className="h-4 w-4" />
                <span className="hidden md:inline">Edit Blocks</span>
              </>
            )}
          </Button>
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

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Side-by-Side PDF Viewers */}
        <div className={`flex-1 grid grid-cols-1 md:grid-cols-2 overflow-hidden transition-all ${showBlocksPanel ? 'md:w-2/3' : 'w-full'}`}>
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

        {/* Blocks Panel */}
        {showBlocksPanel && (
          <div className="w-full md:w-1/3 border-l bg-white overflow-hidden flex flex-col">
            {isLoadingBlocks ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : (
              <BlocksPanel
                blocks={blocks}
                jobId={jobId || ''}
                targetLanguage={targetLanguage}
                onGetAlternatives={handleGetAlternatives}
                onRetranslate={handleRetranslate}
              />
            )}
          </div>
        )}
      </div>

      {/* Tone Customization Section */}
      {showToneSelector && (
        <div className="border-t bg-gray-50 px-4 py-4">
          <ToneSelector
            selectedTone={selectedTone}
            onToneSelect={setSelectedTone}
            disabled={isApplyingTone}
          />
          <div className="flex items-center justify-end gap-3 mt-4">
            <Button
              variant="outline"
              onClick={() => setShowToneSelector(false)}
              disabled={isApplyingTone}
            >
              Cancel
            </Button>
            <Button
              onClick={handleApplyTone}
              disabled={isApplyingTone}
            >
              {isApplyingTone ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  Applying...
                </>
              ) : (
                'Apply Tone'
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Tone Comparison (when available) */}
      {toneComparison && (
        <div className="border-t bg-white px-4 py-4">
          <ToneComparison
            originalText={toneComparison.original}
            customizedText={toneComparison.customized}
            tone={toneComparison.tone}
            costUsd={toneComparison.cost}
            onAccept={handleAcceptTone}
            onReject={handleRejectTone}
          />
        </div>
      )}

      {/* Bottom Action Bar */}
      <div className="border-t bg-white px-4 py-3 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {!showToneSelector && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowToneSelector(true)}
                disabled={isApplyingTone}
              >
                Customize Tone
              </Button>
            )}
            <span className="text-sm text-gray-600">
              Review your translation above. Download when ready.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
