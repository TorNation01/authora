'use client';

import { useState, type KeyboardEvent } from 'react';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { X } from 'lucide-react';

interface TagInputProps {
  value: string[];
  onChange: (tags: string[]) => void;
  placeholder?: string;
  label?: string;
  className?: string;
}

export function TagInput({ value, onChange, placeholder = 'Add...', label, className }: TagInputProps) {
  const [input, setInput] = useState('');

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase();
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed]);
    }
    setInput('');
  };

  const removeTag = (tag: string) => {
    onChange(value.filter((t) => t !== tag));
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag(input);
    } else if (e.key === 'Backspace' && !input && value.length > 0) {
      removeTag(value[value.length - 1]);
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text');
    pasted.split(/[,;\n]+/).forEach((t) => {
      const trimmed = t.trim();
      if (trimmed) addTag(trimmed);
    });
  };

  return (
    <div className={className}>
      {label && <p className="text-sm font-medium mb-2">{label}</p>}
      <div className="flex flex-wrap gap-1.5 p-2 border rounded-md bg-background min-h-[42px] items-center focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-1">
        {value.map((tag) => (
          <Badge key={tag} variant="secondary" className="gap-1 px-2 py-0.5 text-xs">
            {tag}
            <button
              type="button"
              onClick={() => removeTag(tag)}
              className="ml-0.5 rounded-full hover:bg-muted-foreground/20 p-0.5"
            >
              <X className="h-3 w-3" />
            </button>
          </Badge>
        ))}
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          onBlur={() => { if (input.trim()) addTag(input); }}
          placeholder={value.length === 0 ? placeholder : ''}
          className="border-0 shadow-none flex-1 min-w-[120px] h-7 p-0 text-sm focus-visible:ring-0 focus-visible:ring-offset-0"
        />
      </div>
      <p className="text-xs text-muted-foreground mt-1">Type and press Enter or comma to add. Paste multiple separated by commas.</p>
    </div>
  );
}
