import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Loader2, Save, X, Sparkles, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

export interface EditPanelProps {
  blockId: string;
  originalText: string;
  translatedText: string;
  onSave: (text: string) => void;
  onCancel: () => void;
  onGetAlternatives?: () => Promise<string[]>;
  onRetranslate?: (text: string, tone?: string) => Promise<string>;
  maxLength?: number;
}

export function EditPanel({
  blockId,
  originalText,
  translatedText,
  onSave,
  onCancel,
  onGetAlternatives,
  onRetranslate,
  maxLength = 10000,
}: EditPanelProps) {
  const [editedText, setEditedText] = useState(translatedText);
  const [alternatives, setAlternatives] = useState<string[]>([]);
  const [isLoadingAlternatives, setIsLoadingAlternatives] = useState(false);
  const [isRetranslating, setIsRetranslating] = useState(false);
  const [selectedTone, setSelectedTone] = useState<string>('professional');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Focus textarea on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
      // Select all text for easy replacement
      textareaRef.current.setSelectionRange(0, editedText.length);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSave();
      }
      // Escape to cancel
      if (e.key === 'Escape') {
        e.preventDefault();
        handleCancel();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [editedText]);

  const handleSave = () => {
    if (editedText.trim() === translatedText.trim()) {
      toast.info('No changes to save');
      return;
    }
    onSave(editedText);
  };

  const handleCancel = () => {
    if (editedText !== translatedText) {
      // Ask for confirmation if there are unsaved changes
      if (window.confirm('You have unsaved changes. Are you sure you want to cancel?')) {
        setEditedText(translatedText);
        onCancel();
      }
    } else {
      onCancel();
    }
  };

  const handleGetAlternatives = async () => {
    if (!onGetAlternatives) {
      toast.error('Alternatives generation not available');
      return;
    }

    setIsLoadingAlternatives(true);
    try {
      const alts = await onGetAlternatives();
      setAlternatives(alts);
      if (alts.length === 0) {
        toast.info('No alternatives generated');
      }
    } catch (error) {
      console.error('Failed to get alternatives:', error);
      toast.error('Failed to generate alternatives');
    } finally {
      setIsLoadingAlternatives(false);
    }
  };

  const handleSelectAlternative = (alt: string) => {
    setEditedText(alt);
    toast.success('Alternative selected');
  };

  const handleRetranslate = async () => {
    if (!onRetranslate) {
      toast.error('Re-translation not available');
      return;
    }

    setIsRetranslating(true);
    try {
      const retranslated = await onRetranslate(editedText, selectedTone);
      setEditedText(retranslated);
      toast.success('Re-translation complete');
    } catch (error) {
      console.error('Failed to re-translate:', error);
      toast.error('Failed to re-translate');
    } finally {
      setIsRetranslating(false);
    }
  };

  const characterCount = editedText.length;
  const isOverLimit = characterCount > maxLength;
  const hasChanges = editedText.trim() !== translatedText.trim();

  return (
    <Dialog open={true} onOpenChange={(open) => !open && handleCancel()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <span>Edit Translation</span>
            {hasChanges && (
              <span className="text-sm font-normal text-orange-600">
                (Unsaved changes)
              </span>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Original Text (Read-only) */}
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">
              Original Text
            </label>
            <div className="p-3 bg-gray-50 rounded-md border text-sm text-gray-600">
              {originalText}
            </div>
          </div>

          {/* Edited Text */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-gray-700">
                Translated Text
              </label>
              <div className="flex items-center gap-2">
                <span
                  className={`text-xs ${
                    isOverLimit ? 'text-red-600' : 'text-gray-500'
                  }`}
                >
                  {characterCount} / {maxLength} characters
                </span>
              </div>
            </div>
            <Textarea
              ref={textareaRef}
              value={editedText}
              onChange={(e) => setEditedText(e.target.value)}
              className={`min-h-[120px] ${isOverLimit ? 'border-red-500' : ''}`}
              placeholder="Edit the translated text..."
            />
            {isOverLimit && (
              <p className="text-xs text-red-600 mt-1">
                Text exceeds maximum length
              </p>
            )}
          </div>

          {/* Alternatives Section */}
          {onGetAlternatives && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  Alternative Translations
                </label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGetAlternatives}
                  disabled={isLoadingAlternatives}
                  className="gap-2"
                >
                  {isLoadingAlternatives ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4" />
                      Generate Alternatives
                    </>
                  )}
                </Button>
              </div>

              {alternatives.length > 0 && (
                <div className="space-y-2">
                  {alternatives.map((alt, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-blue-50 rounded-md border border-blue-200"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm text-gray-700 flex-1">{alt}</p>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleSelectAlternative(alt)}
                          className="shrink-0"
                        >
                          Use This
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Re-translation Section */}
          {onRetranslate && (
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">
                  Re-translate with Custom Tone
                </label>
                <div className="flex items-center gap-2">
                  <select
                    value={selectedTone}
                    onChange={(e) => setSelectedTone(e.target.value)}
                    className="text-sm border rounded px-2 py-1"
                  >
                    <option value="professional">Professional</option>
                    <option value="casual">Casual</option>
                    <option value="technical">Technical</option>
                    <option value="creative">Creative</option>
                  </select>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleRetranslate}
                    disabled={isRetranslating || !hasChanges}
                    className="gap-2"
                  >
                    {isRetranslating ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Re-translating...
                      </>
                    ) : (
                      <>
                        <RefreshCw className="h-4 w-4" />
                        Re-translate
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleCancel} className="gap-2">
            <X className="h-4 w-4" />
            Cancel
          </Button>
          <Button
            onClick={handleSave}
            disabled={isOverLimit || !hasChanges}
            className="gap-2"
          >
            <Save className="h-4 w-4" />
            Save Changes
          </Button>
        </DialogFooter>

        {/* Keyboard Shortcuts Hint */}
        <div className="text-xs text-gray-500 pt-2 border-t">
          <p>
            <kbd className="px-1.5 py-0.5 bg-gray-100 rounded border">Ctrl/Cmd + S</kbd> to save,{' '}
            <kbd className="px-1.5 py-0.5 bg-gray-100 rounded border">Esc</kbd> to cancel
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
