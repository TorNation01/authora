'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Sparkles, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AIDrawerProps {
  onComplete: (prompt: string, onChunk: (text: string) => void) => Promise<void>;
  onInsert?: (text: string) => void;
  onFictionPrompt?: (promptType: string, onChunk: (text: string) => void, selection?: string) => Promise<void>;
  onNonfictionPrompt?: (promptType: string, onChunk: (text: string) => void, selection?: string) => Promise<void>;
  isFiction?: boolean;
  isNonfiction?: boolean;
  className?: string;
}

const SUGGESTIONS = [
  'Continue this scene with more dialogue',
  'Suggest a plot twist for this chapter',
  'Expand this paragraph with more detail',
  'Help me describe this character',
  'What should happen next?',
];

const NONFICTION_PROMPTS = [
  { type: 'clarify_message', label: 'Clarify message' },
  { type: 'improve_structure', label: 'Improve structure' },
  { type: 'simplify_explanations', label: 'Simplify explanations' },
  { type: 'strengthen_persuasiveness', label: 'Strengthen persuasiveness' },
  { type: 'create_outlines', label: 'Create outlines' },
  { type: 'expand_sections', label: 'Expand sections' },
  { type: 'tone_professional', label: 'More professional tone' },
  { type: 'tone_friendly', label: 'More friendly tone' },
  { type: 'tone_accessible', label: 'More accessible tone' },
  { type: 'create_examples', label: 'Create examples' },
  { type: 'create_analogies', label: 'Create analogies' },
  { type: 'summarize_complex', label: 'Summarize complex material' },
];

const FICTION_PROMPTS = [
  { type: 'alternate_scenes', label: 'Generate alternate scene ideas' },
  { type: 'improve_dialogue', label: 'Improve dialogue' },
  { type: 'deepen_emotion', label: 'Deepen emotion' },
  { type: 'increase_tension', label: 'Increase tension' },
  { type: 'fix_pacing', label: 'Fix pacing' },
  { type: 'rewrite_pov', label: 'Rewrite from another POV' },
  { type: 'suggest_twists', label: 'Suggest plot twists' },
  { type: 'identify_weak', label: 'Identify weak scenes' },
  { type: 'chapter_summary', label: 'Generate chapter summary' },
  { type: 'scene_ideas', label: 'Generate scene ideas' },
  { type: 'what_happens_next', label: 'What happens next?' },
];

export function AIDrawer({ onComplete, onInsert, onFictionPrompt, onNonfictionPrompt, isFiction, isNonfiction, className }: AIDrawerProps) {
  const [prompt, setPrompt] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    if (!prompt.trim()) return;
    setLoading(true);
    setOutput('');
    try {
      await onComplete(prompt, (chunk) => setOutput((s) => s + chunk));
    } finally {
      setLoading(false);
    }
  }

  async function handleFictionPrompt(promptType: string, selection?: string) {
    if (!onFictionPrompt) return;
    setLoading(true);
    setOutput('');
    try {
      await onFictionPrompt(promptType, (chunk) => setOutput((s) => s + chunk), selection);
    } finally {
      setLoading(false);
    }
  }

  async function handleNonfictionPrompt(promptType: string, selection?: string) {
    if (!onNonfictionPrompt) return;
    setLoading(true);
    setOutput('');
    try {
      await onNonfictionPrompt(promptType, (chunk) => setOutput((s) => s + chunk), selection);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className={cn(
        'flex flex-col border-l border-border/60 bg-card/80 w-full sm:max-w-md',
        className
      )}
    >
      <div className="border-b border-border/60 p-4">
        <div className="flex items-center gap-2 text-primary">
          <Sparkles className="h-5 w-5" />
          <h3 className="font-semibold">AI Writing Assistant</h3>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Ask for help. You stay in control—use what works, ignore what doesn&apos;t.
        </p>
      </div>
      <div className="flex-1 overflow-auto p-4 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">What do you need?</label>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Continue this scene with more dialogue..."
            className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            disabled={loading}
          />
        </div>
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setPrompt(s)}
              className="rounded-full bg-muted/80 px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
        {isFiction && onFictionPrompt && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Fiction tools</label>
            <div className="flex flex-wrap gap-2">
              {FICTION_PROMPTS.map((p) => (
                <button
                  key={p.type}
                  type="button"
                  onClick={() => handleFictionPrompt(p.type)}
                  disabled={loading}
                  className="rounded-full bg-primary/10 px-3 py-1.5 text-xs text-primary hover:bg-primary/20 transition-colors"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        )}
        {isNonfiction && onNonfictionPrompt && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Non-fiction tools</label>
            <div className="flex flex-wrap gap-2">
              {NONFICTION_PROMPTS.map((p) => (
                <button
                  key={p.type}
                  type="button"
                  onClick={() => handleNonfictionPrompt(p.type)}
                  disabled={loading}
                  className="rounded-full bg-primary/10 px-3 py-1.5 text-xs text-primary hover:bg-primary/20 transition-colors"
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        )}
        <Button onClick={handleSubmit} disabled={loading} className="w-full">
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="h-4 w-4 mr-2" />
              Generate
            </>
          )}
        </Button>
        {output && (
          <div className="rounded-lg border border-border/60 bg-muted/30 p-4">
            <p className="text-sm font-serif whitespace-pre-wrap leading-relaxed">{output}</p>
            {onInsert && (
              <Button
                variant="soft"
                size="sm"
                className="mt-3"
                onClick={() => onInsert(output)}
              >
                Insert into editor
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
