import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Edit2, CheckCircle2, Circle } from 'lucide-react';
import { useEditStore } from '@/store/editSlice';
import { EditPanel } from './EditPanel';

export interface Block {
  block_id: string;
  page_num: number;
  block_num: number;
  original_text: string;
  translated_text: string;
  tone_customized_text?: string;
}

export interface BlocksPanelProps {
  blocks: Block[];
  jobId: string;
  targetLanguage: string;
  onGetAlternatives?: (text: string) => Promise<string[]>;
  onRetranslate?: (text: string, tone: string) => Promise<string>;
}

export function BlocksPanel({
  blocks,
  jobId,
  targetLanguage,
  onGetAlternatives,
  onRetranslate,
}: BlocksPanelProps) {
  const [selectedBlock, setSelectedBlock] = useState<Block | null>(null);
  const { edits, getEdit } = useEditStore();

  const handleBlockClick = (block: Block) => {
    setSelectedBlock(block);
  };

  const { setEdit } = useEditStore();

  const handleSaveEdit = (blockId: string, editedText: string) => {
    const block = blocks.find(b => b.block_id === blockId);
    if (block) {
      setEdit(blockId, block.original_text, editedText);
      setSelectedBlock(null);
    }
  };

  const handleCancelEdit = () => {
    setSelectedBlock(null);
  };

  const getDisplayText = (block: Block): string => {
    const edit = getEdit(block.block_id);
    if (edit) {
      return edit.editedText;
    }
    // Use tone-customized text if available, otherwise translated text
    return block.tone_customized_text || block.translated_text;
  };

  const isBlockEdited = (blockId: string): boolean => {
    return !!getEdit(blockId);
  };

  return (
    <>
      <Card className="p-4 h-full overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Translation Blocks</h3>
          <span className="text-sm text-gray-500">
            {blocks.length} blocks
          </span>
        </div>

        <div className="space-y-2">
          {blocks.map((block) => {
            const displayText = getDisplayText(block);
            const isEdited = isBlockEdited(block.block_id);
            const isSelected = selectedBlock?.block_id === block.block_id;

            return (
              <div
                key={block.block_id}
                className={`
                  p-3 rounded-lg border cursor-pointer transition-all
                  ${isSelected 
                    ? 'border-primary bg-primary/5' 
                    : 'border-gray-200 hover:border-gray-300'
                  }
                  ${isEdited ? 'bg-yellow-50 border-yellow-300' : ''}
                `}
                onClick={() => handleBlockClick(block)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-500">
                        Page {block.page_num + 1}, Block {block.block_num + 1}
                      </span>
                      {isEdited && (
                        <span className="text-xs bg-yellow-200 text-yellow-800 px-2 py-0.5 rounded">
                          Edited
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2">
                      {displayText || '(No translation)'}
                    </p>
                  </div>
                  <div className="flex items-center gap-1">
                    {isEdited ? (
                      <CheckCircle2 className="h-4 w-4 text-yellow-600" />
                    ) : (
                      <Circle className="h-4 w-4 text-gray-300" />
                    )}
                    <Edit2 className="h-4 w-4 text-gray-400" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      {selectedBlock && (
        <EditPanel
          blockId={selectedBlock.block_id}
          originalText={selectedBlock.original_text}
          translatedText={getDisplayText(selectedBlock)}
          onSave={(text) => handleSaveEdit(selectedBlock.block_id, text)}
          onCancel={handleCancelEdit}
          onGetAlternatives={onGetAlternatives ? () => 
            onGetAlternatives(selectedBlock.translated_text) : undefined
          }
          onRetranslate={onRetranslate ? (text, tone) =>
            onRetranslate(text, tone) : undefined
          }
        />
      )}
    </>
  );
}
