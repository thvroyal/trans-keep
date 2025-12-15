import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Check, X, Sparkles, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

interface ToneComparisonProps {
  originalText: string;
  customizedText: string | null;
  tone: string;
  isLoading?: boolean;
  onAccept: () => void;
  onReject: () => void;
  costUsd?: number;
}

export function ToneComparison({
  originalText,
  customizedText,
  tone,
  isLoading = false,
  onAccept,
  onReject,
  costUsd,
}: ToneComparisonProps) {
  const [showDiff, setShowDiff] = useState(true);

  // Simple diff highlighting (word-level)
  const highlightDifferences = (original: string, customized: string) => {
    if (!customized) return { original, customized: '' };
    
    const originalWords = original.split(/(\s+)/);
    const customizedWords = customized.split(/(\s+)/);
    
    // Simple word-by-word comparison
    const maxLen = Math.max(originalWords.length, customizedWords.length);
    const originalHighlighted: string[] = [];
    const customizedHighlighted: string[] = [];
    
    for (let i = 0; i < maxLen; i++) {
      const origWord = originalWords[i] || '';
      const customWord = customizedWords[i] || '';
      
      if (origWord !== customWord && origWord.trim() && customWord.trim()) {
        originalHighlighted.push(`<span class="bg-red-100 line-through">${origWord}</span>`);
        customizedHighlighted.push(`<span class="bg-green-100 font-medium">${customWord}</span>`);
      } else {
        originalHighlighted.push(origWord);
        customizedHighlighted.push(customWord);
      }
    }
    
    return {
      original: originalHighlighted.join(''),
      customized: customizedHighlighted.join(''),
    };
  };

  const diff = customizedText
    ? highlightDifferences(originalText, customizedText)
    : { original: originalText, customized: '' };

  if (isLoading) {
    return (
      <Card className="p-6">
        <div className="flex items-center gap-3 mb-4">
          <Loader2 className="h-5 w-5 animate-spin text-primary" />
          <h3 className="text-lg font-semibold">Applying Tone Customization...</h3>
        </div>
        <p className="text-sm text-gray-600">
          Processing your translation with "{tone}" tone. This may take a moment.
        </p>
      </Card>
    );
  }

  if (!customizedText) {
    return null;
  }

  return (
    <Card className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Tone Customization Preview</h3>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowDiff(!showDiff)}
          >
            {showDiff ? 'Hide' : 'Show'} Differences
          </Button>
          {costUsd && (
            <span className="text-sm text-gray-600">
              Cost: ${costUsd.toFixed(4)}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Original Translation */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-700">Original Translation</span>
          </div>
          <div className="p-3 bg-gray-50 rounded border border-gray-200 min-h-[150px] max-h-[300px] overflow-y-auto">
            {showDiff ? (
              <div
                className="text-sm text-gray-800 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: diff.original }}
              />
            ) : (
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{originalText}</p>
            )}
          </div>
        </div>

        {/* Tone-Customized Translation */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-primary">With "{tone}" Tone</span>
          </div>
          <div className="p-3 bg-blue-50 rounded border border-blue-200 min-h-[150px] max-h-[300px] overflow-y-auto">
            {showDiff ? (
              <div
                className="text-sm text-gray-800 whitespace-pre-wrap"
                dangerouslySetInnerHTML={{ __html: diff.customized }}
              />
            ) : (
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{customizedText}</p>
            )}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t">
        <Button
          variant="outline"
          onClick={onReject}
          className="gap-2"
        >
          <X className="h-4 w-4" />
          Keep Original
        </Button>
        <Button
          onClick={onAccept}
          className="gap-2"
        >
          <Check className="h-4 w-4" />
          Accept Customized
        </Button>
      </div>

      {/* Legend for diff highlighting */}
      {showDiff && (
        <div className="flex items-center gap-4 text-xs text-gray-600 pt-2 border-t">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-red-100 border border-red-300 rounded"></span>
            <span>Removed</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-green-100 border border-green-300 rounded"></span>
            <span>Added</span>
          </div>
        </div>
      )}
    </Card>
  );
}

