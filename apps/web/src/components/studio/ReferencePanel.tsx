'use client';

import { useState } from 'react';
import { Loader2, AlertCircle } from 'lucide-react';
import { useReferencePanelData } from '@/hooks/useReferencePanelData';
import { cn } from '@/lib/utils';

interface ReferencePanelProps {
  lookupWord?: string | null;
  documentText?: string;
  onWordSelect?: (word: string) => void;
  onReplace?: (from: string, to: string) => void;
  activeTab?: 'lookup' | 'analysis';
  onActiveTabChange?: (tab: 'lookup' | 'analysis') => void;
  className?: string;
}

export function ReferencePanel({
  lookupWord,
  documentText,
  onWordSelect,
  onReplace,
  activeTab: activeTabProp,
  onActiveTabChange,
  className,
}: ReferencePanelProps) {
  const { lookupResult, analysisResult, loading, error } = useReferencePanelData(lookupWord, documentText);
  const [internalTab, setInternalTab] = useState<'lookup' | 'analysis'>('lookup');
  const activeTab = activeTabProp != null ? activeTabProp : internalTab;
  const setActiveTab = (tab: 'lookup' | 'analysis') => {
    onActiveTabChange?.(tab);
    if (activeTabProp == null) setInternalTab(tab);
  };

  const rootClassName = cn('flex flex-col border-l bg-card w-80', className);
  return (
    <div className={rootClassName}>
      <div className="flex border-b">
        <button
          type="button"
          onClick={() => setActiveTab('lookup')}
          className={cn(
            'flex-1 py-3 text-sm font-medium',
            activeTab === 'lookup' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground'
          )}
        >
          Lookup
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('analysis')}
          className={cn(
            'flex-1 py-3 text-sm font-medium',
            activeTab === 'analysis' ? 'border-b-2 border-primary text-primary' : 'text-muted-foreground'
          )}
        >
          Analysis
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {error && (
          <div className="flex items-center gap-2 text-sm text-destructive mb-3">
            <AlertCircle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        {activeTab === 'lookup' && (
          <div className="space-y-4">
            {!lookupWord ? (
              <p className="text-sm text-muted-foreground">
                Select a word or right-click to look up.
              </p>
            ) : loading && !lookupResult ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Looking up...
              </div>
            ) : lookupResult ? (
              <>
                <div>
                  <h4 className="font-semibold text-lg">{lookupResult.word}</h4>
                  {lookupResult.definition?.phonetic && (
                    <p className="text-sm text-muted-foreground">{lookupResult.definition.phonetic}</p>
                  )}
                </div>
                {lookupResult.definition?.meanings?.length ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Definitions</h5>
                    <ul className="space-y-2 text-sm">
                      {lookupResult.definition.meanings.slice(0, 3).map((m, i) => (
                        <li key={i}>
                          <span className="text-muted-foreground">{m.partOfSpeech}</span>
                          {m.definitions?.slice(0, 2).map((d, j) => (
                            <p key={j} className="mt-1">{d.definition}</p>
                          ))}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {lookupResult.synonyms.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Synonyms</h5>
                    <div className="flex flex-wrap gap-1">
                      {lookupResult.synonyms.slice(0, 12).map((s) => (
                        <button
                          key={s}
                          type="button"
                          onClick={() => onReplace?.(lookupResult.word, s)}
                          className="rounded bg-muted px-2 py-0.5 text-xs hover:bg-primary/20 transition-colors"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
                {lookupResult.antonyms.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Antonyms</h5>
                    <div className="flex flex-wrap gap-1">
                      {lookupResult.antonyms.slice(0, 8).map((a) => (
                        <button
                          key={a}
                          type="button"
                          onClick={() => onReplace?.(lookupResult.word, a)}
                          className="rounded bg-muted px-2 py-0.5 text-xs hover:bg-primary/20 transition-colors"
                        >
                          {a}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
                {lookupResult.simplification_hint ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Simpler</h5>
                    <button
                      type="button"
                      onClick={() => onReplace?.(lookupResult.word, lookupResult.simplification_hint!)}
                      className="rounded bg-amber-100 dark:bg-amber-900/30 px-2 py-2 text-sm hover:bg-amber-200 dark:hover:bg-amber-900/50"
                    >
                      Try &quot;{lookupResult.simplification_hint}&quot;
                    </button>
                  </div>
                ) : null}
                {lookupResult.vocab_alternatives.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Richer alternatives</h5>
                    <div className="flex flex-wrap gap-1">
                      {lookupResult.vocab_alternatives.slice(0, 8).map((v) => (
                        <button
                          key={v}
                          type="button"
                          onClick={() => onReplace?.(lookupResult.word, v)}
                          className="rounded bg-muted px-2 py-0.5 text-xs hover:bg-primary/20 transition-colors"
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </>
            ) : null}
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="space-y-4">
            {!documentText ? (
              <p className="text-sm text-muted-foreground">
                Add content to analyze overused words, repeated phrases, and more.
              </p>
            ) : loading && !analysisResult ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing...
              </div>
            ) : analysisResult ? (
              <>
                {analysisResult.overused_words.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Overused words</h5>
                    <div className="flex flex-wrap gap-1">
                      {analysisResult.overused_words.slice(0, 10).map(({ word, count }) => (
                        <button
                          key={word}
                          type="button"
                          onClick={() => onWordSelect?.(word)}
                          className="rounded bg-amber-100 dark:bg-amber-900/30 px-2 py-0.5 text-xs"
                        >
                          {word} ({count})
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
                {analysisResult.repeated_phrases.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Repeated phrases</h5>
                    <ul className="text-sm space-y-1">
                      {analysisResult.repeated_phrases.slice(0, 5).map(({ phrase, count }) => (
                        <li key={phrase}>{phrase} ({count}x)</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {analysisResult.cliches.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Cliches</h5>
                    <ul className="text-sm space-y-1">
                      {analysisResult.cliches.map(({ phrase }) => (
                        <li key={phrase}>{phrase}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {analysisResult.readability_hints.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Simplification hints</h5>
                    <ul className="text-sm space-y-1">
                      {analysisResult.readability_hints.slice(0, 5).map(({ word, suggestion }) => (
                        <li key={word}>
                          &quot;{word}&quot; → &quot;{suggestion}&quot;
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {analysisResult.vocab_enhancements.length > 0 ? (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground uppercase mb-2">Vocabulary enhancement</h5>
                    <ul className="text-sm space-y-1">
                      {analysisResult.vocab_enhancements.slice(0, 5).map(({ word, alternatives }) => (
                        <li key={word}>
                          &quot;{word}&quot;: {alternatives.slice(0, 3).join(', ')}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {!analysisResult.overused_words.length &&
                  !analysisResult.repeated_phrases.length &&
                  !analysisResult.cliches.length &&
                  !analysisResult.readability_hints.length &&
                  !analysisResult.vocab_enhancements.length ? (
                    <p className="text-sm text-muted-foreground">No issues detected.</p>
                  ) : null}
              </>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
