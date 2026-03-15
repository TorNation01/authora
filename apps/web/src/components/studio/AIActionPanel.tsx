'use client';

import { useState, useEffect } from 'react';
import { Sparkles, Loader2, Settings2, RefreshCw, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { AI_MODES, ASSISTANCE_LEVELS, type AIAction, type AIModeId, type AssistanceLevelId } from '@authora/shared';
import { api } from '@/lib/api';

interface AIActionPanelProps {
  projectId?: string;
  bookId: string;
  bookType?: 'fiction' | 'nonfiction';
  chapterId?: string;
  selection?: string;
  onOutput: (text: string) => void;
  onInsert?: (text: string) => void;
  className?: string;
}

export function AIActionPanel({
  projectId,
  bookId,
  bookType = 'general',
  chapterId,
  selection,
  onOutput,
  onInsert,
  className,
}: AIActionPanelProps) {
  const [actions, setActions] = useState<AIAction[]>([]);
  const [mode, setMode] = useState<AIModeId>('assist');
  const [level, setLevel] = useState<AssistanceLevelId>('moderate');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [rewriteFeedback, setRewriteFeedback] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/ai/actions`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then((r) => r.json())
      .then(setActions)
      .catch(() => setActions([]));
  }, []);

  async function runAction(actionId: string) {
    setLoading(true);
    setOutput('');
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/ai/actions/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          action_id: actionId,
          book_id: bookId,
          chapter_id: chapterId || null,
          selection: selection || '',
          context: selection || '',
          mode,
          level,
          book_type: bookType === 'fiction' ? 'fiction' : bookType === 'nonfiction' ? 'nonfiction' : 'general',
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || res.statusText);
      }
      const reader = res.body?.getReader();
      if (!reader) throw new Error('No response body');
      const decoder = new TextDecoder();
      let text = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        text += chunk;
        setOutput(text);
        onOutput(text);
      }
    } catch (err) {
      setOutput(err instanceof Error ? err.message : 'AI request failed');
    } finally {
      setLoading(false);
    }
  }

  async function runRegenerate() {
    if (!selection || !projectId) return;
    setLoading(true);
    setOutput('');
    try {
      const { text } = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/regenerate`,
        { method: 'POST', body: JSON.stringify({ selection }) }
      );
      setOutput(text);
      onOutput(text);
    } catch (err) {
      setOutput(err instanceof Error ? err.message : 'Regenerate failed');
    } finally {
      setLoading(false);
    }
  }

  async function runRewriteWithFeedback() {
    if (!selection || !rewriteFeedback.trim() || !projectId) return;
    setLoading(true);
    setOutput('');
    try {
      const { text } = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/rewrite-with-feedback`,
        { method: 'POST', body: JSON.stringify({ selection, feedback: rewriteFeedback }) }
      );
      setOutput(text);
      onOutput(text);
    } catch (err) {
      setOutput(err instanceof Error ? err.message : 'Rewrite failed');
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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-primary">
            <Sparkles className="h-5 w-5" />
            <h3 className="font-semibold">AI Writing Assistant</h3>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowSettings((s) => !s)}
          >
            <Settings2 className="h-4 w-4" />
          </Button>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">
          Provider-agnostic. Preserve your voice. Accept or reject suggestions.
        </p>
      </div>

      {showSettings && (
        <div className="border-b border-border/60 p-4 space-y-4">
          <div>
            <label className="text-xs font-medium text-muted-foreground">Mode</label>
            <div className="flex flex-wrap gap-1 mt-1">
              {AI_MODES.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setMode(m.id)}
                  className={cn(
                    'rounded-full px-2.5 py-1 text-xs transition-colors',
                    mode === m.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted/80 text-muted-foreground hover:bg-muted'
                  )}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="text-xs font-medium text-muted-foreground">Assistance level</label>
            <div className="flex flex-wrap gap-1 mt-1">
              {ASSISTANCE_LEVELS.map((l) => (
                <button
                  key={l.id}
                  type="button"
                  onClick={() => setLevel(l.id)}
                  className={cn(
                    'rounded-full px-2.5 py-1 text-xs transition-colors',
                    level === l.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted/80 text-muted-foreground hover:bg-muted'
                  )}
                >
                  {l.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-auto p-4 space-y-4">
        <div className="space-y-2">
          <label className="text-sm font-medium">Actions</label>
          {projectId && selection && (
            <div className="flex flex-wrap gap-2 mb-2">
              <Button
                variant="outline"
                size="sm"
                onClick={runRegenerate}
                disabled={loading}
                className="gap-1"
              >
                <RefreshCw className="h-3 w-3" />
                Regenerate section
              </Button>
              <div className="flex gap-1 flex-1 min-w-0">
                <Input
                  placeholder="e.g. Make it warmer, more concise, or more formal..."
                  value={rewriteFeedback}
                  onChange={(e) => setRewriteFeedback(e.target.value)}
                  className="flex-1 min-w-0 text-sm"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={runRewriteWithFeedback}
                  disabled={loading || !rewriteFeedback.trim()}
                  className="gap-1 shrink-0"
                >
                  <MessageSquare className="h-3 w-3" />
                  Rewrite
                </Button>
              </div>
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            {actions.slice(0, 12).map((a) => (
              <button
                key={a.id}
                type="button"
                onClick={() => runAction(a.id)}
                disabled={loading || (a.uses_selection && !selection)}
                className="rounded-full bg-primary/10 px-3 py-1.5 text-xs text-primary hover:bg-primary/20 transition-colors disabled:opacity-50"
              >
                {a.label}
              </button>
            ))}
          </div>
        </div>

        {output && (
          <div className="rounded-lg border border-border/60 bg-muted/30 p-4">
            <p className="text-xs font-medium text-muted-foreground mb-2">AI suggestion</p>
            <p className="text-sm font-serif whitespace-pre-wrap leading-relaxed">{output}</p>
            {onInsert && (
              <div className="flex gap-2 mt-3">
                <Button variant="default" size="sm" onClick={() => onInsert(output)}>
                  Accept
                </Button>
                <Button variant="outline" size="sm" onClick={() => setOutput('')}>
                  Reject
                </Button>
              </div>
            )}
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Generating...
          </div>
        )}
      </div>
    </div>
  );
}
