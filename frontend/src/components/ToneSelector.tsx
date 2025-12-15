import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Sparkles, Briefcase, Users, Code, Palette, Edit3 } from 'lucide-react';

export type TonePreset = 'professional' | 'casual' | 'technical' | 'creative' | 'custom';

export interface ToneSelectorProps {
  selectedTone: TonePreset | string;
  onToneSelect: (tone: TonePreset | string) => void;
  disabled?: boolean;
  showCustomInput?: boolean;
}

const TONE_PRESETS = [
  {
    id: 'professional' as TonePreset,
    label: 'Professional',
    description: 'Formal business language',
    icon: Briefcase,
    color: 'bg-blue-500 hover:bg-blue-600',
  },
  {
    id: 'casual' as TonePreset,
    label: 'Casual',
    description: 'Friendly, conversational',
    icon: Users,
    color: 'bg-green-500 hover:bg-green-600',
  },
  {
    id: 'technical' as TonePreset,
    label: 'Technical',
    description: 'For documentation',
    icon: Code,
    color: 'bg-purple-500 hover:bg-purple-600',
  },
  {
    id: 'creative' as TonePreset,
    label: 'Creative',
    description: 'For marketing',
    icon: Palette,
    color: 'bg-pink-500 hover:bg-pink-600',
  },
  {
    id: 'custom' as TonePreset,
    label: 'Custom',
    description: 'User-defined tone',
    icon: Edit3,
    color: 'bg-gray-500 hover:bg-gray-600',
  },
];

export function ToneSelector({
  selectedTone,
  onToneSelect,
  disabled = false,
  showCustomInput = true,
}: ToneSelectorProps) {
  const [customTone, setCustomTone] = useState<string>('');

  const handlePresetClick = (preset: TonePreset) => {
    if (!disabled) {
      onToneSelect(preset);
    }
  };

  const handleCustomToneChange = (value: string) => {
    setCustomTone(value);
    if (value.trim()) {
      onToneSelect(value);
    } else {
      onToneSelect('professional'); // Default fallback
    }
  };

  const isCustomSelected = selectedTone === 'custom' || 
    (!TONE_PRESETS.some(p => p.id === selectedTone) && selectedTone !== '');

  return (
    <Card className="p-4 space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Tone Customization</h3>
      </div>

      {/* Preset Buttons */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
        {TONE_PRESETS.map((preset) => {
          const Icon = preset.icon;
          const isSelected = selectedTone === preset.id;
          
          return (
            <button
              key={preset.id}
              onClick={() => handlePresetClick(preset.id)}
              disabled={disabled}
              className={`
                flex flex-col items-center gap-2 p-3 rounded-lg border-2 transition-all
                ${isSelected 
                  ? 'border-primary bg-primary/10' 
                  : 'border-gray-200 hover:border-gray-300 bg-white'
                }
                ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className={`
                p-2 rounded-full text-white
                ${isSelected ? preset.color : 'bg-gray-400'}
              `}>
                <Icon className="h-4 w-4" />
              </div>
              <div className="text-center">
                <div className={`text-sm font-medium ${isSelected ? 'text-primary' : 'text-gray-700'}`}>
                  {preset.label}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">
                  {preset.description}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Custom Tone Input */}
      {showCustomInput && (
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">
            Custom Tone Description
          </label>
          <Input
            type="text"
            placeholder="e.g., Friendly but professional, Academic, Marketing copy..."
            value={customTone}
            onChange={(e) => handleCustomToneChange(e.target.value)}
            disabled={disabled}
            className={isCustomSelected ? 'border-primary' : ''}
          />
          {isCustomSelected && customTone && (
            <p className="text-xs text-gray-500">
              Selected: "{customTone}"
            </p>
          )}
        </div>
      )}

      {/* Selected Tone Preview */}
      {selectedTone && !isCustomSelected && (
        <div className="mt-2 p-2 bg-primary/5 rounded border border-primary/20">
          <p className="text-sm text-gray-700">
            <span className="font-medium">Selected:</span>{' '}
            {TONE_PRESETS.find(p => p.id === selectedTone)?.label || selectedTone}
          </p>
        </div>
      )}
    </Card>
  );
}

