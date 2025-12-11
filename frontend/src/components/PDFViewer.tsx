import { useEffect, useRef, useState, useCallback } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import { ZoomIn, ZoomOut } from 'lucide-react';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.8.162/pdf.worker.min.js`;

interface PDFViewerProps {
  pdfUrl: string;
  onScroll?: (scrollTop: number) => void;
  syncedScrollPosition?: number;
  className?: string;
}

export function PDFViewer({ pdfUrl, onScroll, syncedScrollPosition, className = '' }: PDFViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const pageRefsMap = useRef<Map<number, HTMLCanvasElement>>(new Map());
  const renderTasksRef = useRef<Map<number, any>>(new Map());
  const [pdf, setPdf] = useState<pdfjsLib.PDFDocumentProxy | null>(null);
  const [currentVisiblePage, setCurrentVisiblePage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [zoom, setZoom] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [canvasesMounted, setCanvasesMounted] = useState(0);

  // Load PDF document
  useEffect(() => {
    const loadPdf = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const loadingTask = pdfjsLib.getDocument(pdfUrl);
        const pdfDoc = await loadingTask.promise;
        
        setPdf(pdfDoc);
        setTotalPages(pdfDoc.numPages);
        setIsLoading(false);
      } catch (err) {
        console.error('Error loading PDF:', err);
        setError('Failed to load PDF');
        setIsLoading(false);
      }
    };

    if (pdfUrl) {
      loadPdf();
    }

    // Cleanup render tasks on unmount
    return () => {
      renderTasksRef.current.forEach((task: any) => {
        if (task) {
          task.cancel();
        }
      });
      renderTasksRef.current.clear();
    };
  }, [pdfUrl]);

  // Render a specific page
  const renderPage = useCallback(async (pageNum: number) => {
    if (!pdf) return;

    const canvas = pageRefsMap.current.get(pageNum);
    if (!canvas) return;

    try {
      // Cancel previous render task for this page if still in progress
      const existingTask = renderTasksRef.current.get(pageNum);
      if (existingTask) {
        existingTask.cancel();
      }

      const page = await pdf.getPage(pageNum);
      const context = canvas.getContext('2d');
      
      if (!context) return;

      const viewport = page.getViewport({ scale: zoom });
      
      // Set canvas dimensions
      canvas.width = viewport.width;
      canvas.height = viewport.height;

      // Render PDF page
      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };

      const renderTask = page.render(renderContext);
      renderTasksRef.current.set(pageNum, renderTask);
      
      await renderTask.promise;
      
      renderTasksRef.current.delete(pageNum);
    } catch (err) {
      if ((err as any)?.name === 'RenderingCancelledException') {
        return; // Ignore cancelled renders
      }
      console.error(`Error rendering page ${pageNum}:`, err);
    }
  }, [pdf, zoom]);

  // Render all pages when PDF loads or zoom changes
  useEffect(() => {
    if (!pdf || totalPages === 0) return;

    // Render all pages
    const renderAllPages = async () => {
      for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        await renderPage(pageNum);
      }
    };

    renderAllPages();
  }, [pdf, totalPages, zoom, renderPage]);

  // Intersection Observer to track current visible page
  useEffect(() => {
    if (!containerRef.current || totalPages === 0) return;
    
    // Wait for canvases to be mounted in the DOM
    if (canvasesMounted < totalPages) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const pageNum = parseInt(entry.target.getAttribute('data-page-number') || '1');
            setCurrentVisiblePage(pageNum);
          }
        });
      },
      {
        root: containerRef.current,
        threshold: 0.5, // Page is considered visible when 50% is in view
      }
    );

    // Observe all page canvases
    pageRefsMap.current.forEach((canvas: HTMLCanvasElement) => {
      observer.observe(canvas);
    });

    return () => {
      observer.disconnect();
    };
  }, [totalPages, canvasesMounted]);

  // Handle scroll synchronization
  useEffect(() => {
    if (syncedScrollPosition !== undefined && containerRef.current) {
      containerRef.current.scrollTop = syncedScrollPosition;
    }
  }, [syncedScrollPosition]);

  // Handle scroll events
  const handleScroll = () => {
    if (containerRef.current && onScroll) {
      onScroll(containerRef.current.scrollTop);
    }
  };

  // Zoom handlers
  const zoomIn = () => {
    setZoom(Math.min(zoom + 0.2, 3));
  };

  const zoomOut = () => {
    setZoom(Math.max(zoom - 0.2, 0.5));
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading PDF...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`flex items-center justify-center h-full ${className}`}>
        <div className="text-center text-red-600">
          <p className="font-semibold">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative h-full ${className}`}>
      {/* PDF Pages - Continuous Scroll */}
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="h-full overflow-auto bg-gray-200 p-4 pb-20"
      >
        <div className="flex flex-col items-center gap-4">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
            <canvas
              key={pageNum}
              ref={(el: HTMLCanvasElement | null) => {
                if (el) {
                  pageRefsMap.current.set(pageNum, el);
                  setCanvasesMounted(pageRefsMap.current.size);
                } else {
                  pageRefsMap.current.delete(pageNum);
                  setCanvasesMounted(pageRefsMap.current.size);
                }
              }}
              data-page-number={pageNum}
              className="shadow-lg bg-white min-h-[600px]"
            />
          ))}
        </div>
      </div>

      {/* Floating Toolbar - Bottom */}
      <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-white/95 backdrop-blur-sm rounded-full shadow-lg border border-gray-200 px-4 py-2">
        <div className="flex items-center gap-4">
          {/* Page Indicator */}
          <span className="text-sm font-medium text-gray-700">
            {currentVisiblePage} / {totalPages}
          </span>
          
          <div className="h-4 w-px bg-gray-300" />
          
          {/* Zoom Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={zoomOut}
              className="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
              title="Zoom out"
            >
              <ZoomOut className="h-4 w-4 text-gray-600" />
            </button>
            
            <span className="text-xs font-medium text-gray-600 min-w-12 text-center">
              {Math.round(zoom * 100)}%
            </span>
            
            <button
              onClick={zoomIn}
              className="p-1.5 rounded-full hover:bg-gray-100 transition-colors"
              title="Zoom in"
            >
              <ZoomIn className="h-4 w-4 text-gray-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

