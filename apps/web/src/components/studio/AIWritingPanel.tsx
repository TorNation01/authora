'use client';

import { useState } from 'react';
import { Sparkles, Zap, MessageSquare } from 'lucide-react';
import { AIActionPanel } from './AIActionPanel';
import { AIDrawer } from './AIDrawer';
import { GhostwriterQuestionnaire } from './GhostwriterQuestionnaire';
import { CompareVersionsDialog } from './CompareVersionsDialog';
import { cn } from '@/lib/utils';

type TabId = 'actions' | 'prompts' | 'ghostwriter';

interface AIWritingPanelProps {
  projectId?: string;
  bookId: string;
  bookType?: 'fiction' | 'nonfiction';
  chapterId?: string;
  selection?: string;
  onComplete?: (prompt: string, onChunk: (text: string) => void) => Promise<void>;
  onFictionPrompt?: (promptType: string, selection?: string, onChunk: (text: string) => void) => Promise<void>;
  onNonfictionPrompt?: (promptType: string, selection?: string, onChunk: (text: string) => void) => Promise<void>;
  onInsert?: (text: string) => void;
  isFiction?: boolean;
  isNonfiction?: boolean;
  className?: string;
}

export function AIWritingPanel({
  bookId,
  bookType,
  chapterId,
  selection,
  onComplete,
  onFictionPrompt,
  onNonfictionPrompt,
  onInsert,
  isFiction,
  isNonfiction,
  className,
}: AIWritingPanelProps) {
  const [tab, setTab] = useState<TabId>('actions');
  const [ghostwriterOutput, setGhostwriterOutput] = useState('');
  const [compareOriginal, setCompareOriginal] = useState('');
  const [compareSuggested, setCompareSuggested] = useState('');
  const [showCompare, setShowCompare] = useState(false);
  const [ghostwriterLoading, setGhostwriterLoading] = useState(false);

  function handleInsert(text: string) {
    onInsert?.(text);
  }

  function handleAcceptSuggestion() {
    if (compareSuggested) onInsert?.(compareSuggested);
    setShowCompare(false);
  }

  async function handleGhostwriterGenerate(answers: Record<string, string>) {
    setGhostwriterLoading(true);
    setGhostwriterOutput('');
    try {
      const context = Object.entries(answers)
        .map(([k, v]) => `${k}: ${v}`)
        .join('\n');
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/ai/actions/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          action_id: 'generate_section',
          book_id: bookId,
          chapter_id: chapterId || null,
          context,
          mode: 'ghostwriter',
          level: 'creative',
          book_type: bookType === 'fiction' ? 'fiction' : bookType === 'nonfiction' ? 'nonfiction' : 'general',
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const reader = res.body?.getReader();
      if (!reader) return;
      const decoder = new TextDecoder();
      let text = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += decoder.decode(value, { stream: true });
        setGhostwriterOutput(text);
      }
    } catch (err) {
      setGhostwriterOutput(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setGhostwriterLoading(false);
    }
  }

  return (
    <div className={cn('flex flex-col border-l bg-card/80 w-full sm:max-w-md', className)}>
      <div className="flex border-b">
        <button
          type="button"
          onClick={() => setTab('actions')}
          className={cn(
            'flex-1 flex items-center justify-center gap-1.5 py-3 text-sm font-medium transition-colors',
            tab === 'actions' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Zap className="h-4 w-4" />
          Actions
        </button>
        <button
          type="button"
          onClick={() => setTab('prompts')}
          className={cn(
            'flex-1 flex items-center justify-center gap-1.5 py-3 text-sm font-medium transition-colors',
            tab === 'prompts' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <MessageSquare className="h-4 w-4" />
          Prompts
        </button>
        <button
          type="button"
          onClick={() => setTab('ghostwriter')}
          className={cn(
            'flex-1 flex items-center justify-center gap-1.5 py-3 text-sm font-medium transition-colors',
            tab === 'ghostwriter' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground hover:text-foreground'
          )}
        >
          <Sparkles className="h-4 w-4" />
          Ghostwriter
        </button>
      </div>

      <div className="flex-1 overflow-auto">
        {tab === 'actions' && (
          <AIActionPanel
            projectId={projectId}
            bookId={bookId}
            bookType={bookType}
            chapterId={chapterId}
            selection={selection}
            onOutput={() => {}}
            onInsert={handleInsert}
          />
        )}
        {tab === 'prompts' && (
          <AIDrawer
            onComplete={onComplete ?? (async () => {})}
            onInsert={onInsert}
            onFictionPrompt={onFictionPrompt}
            onNonfictionPrompt={onNonfictionPrompt}
            isFiction={isFiction}
            isNonfiction={isNonfiction}
          />
        )}
        {tab === 'ghostwriter' && (
          <div className="p-4">
            <GhostwriterQuestionnaire
              onGenerate={handleGhostwriterGenerate}
              onOutput={() => {}}
              loading={ghostwriterLoading}
            />
            {ghostwriterOutput && (
              <div className="mt-4 rounded-lg border bg-muted/30 p-4">
                <p className="text-sm font-serif whitespace-pre-wrap">{ghostwriterOutput}</p>
                <div className="flex gap-2 mt-3">
                  <button
                    type="button"
                    className="text-sm text-primary hover:underline"
                    onClick={() => {
                      setCompareOriginal('');
                      setCompareSuggested(ghostwriterOutput);
                      setShowCompare(true);
                    }}
                  >
                    Compare
                  </button>
                  <button
                    type="button"
                    className="text-sm text-primary hover:underline"
                    onClick={() => handleInsert(ghostwriterOutput)}
                  >
                    Accept
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <CompareVersionsDialog
        open={showCompare}
        onOpenChange={setShowCompare}
        original={compareOriginal}
        suggested={compareSuggested}
        onAccept={handleAcceptSuggestion}
        onReject={() => setShowCompare(false)}
      />
    </div>
  );
}
