'use client';

import { useState, useEffect } from 'react';
import type { Editor } from '@tiptap/react';
import { BubbleMenu } from '@tiptap/react';
import { BookOpen, Loader2 } from 'lucide-react';
import { useReference } from '@/hooks/useReference';
import { cn } from '@/lib/utils';

interface ReferenceBubbleMenuProps {
  editor: Editor | null;
  onLookup?: (word: string) => void;
}

export function ReferenceBubbleMenu({ editor, onLookup }: ReferenceBubbleMenuProps) {
  const { getSynonyms } = useReference();
  const [synonyms, setSynonyms] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedWord, setSelectedWord] = useState('');

  useEffect(() => {
    if (!editor) return;
    const handler = async () => {
      const { from, to } = editor.state.selection;
      const text = editor.state.doc.textBetween(from, to).trim();
      const words = text.split(/\s+/);
      if (words.length === 1 && /^[a-zA-Z']+$/.test(words[0])) {
        setSelectedWord(words[0]);
        setLoading(true);
        try {
          const syns = await getSynonyms(words[0]);
          setSynonyms(syns);
        } catch {
          setSynonyms([]);
        } finally {
          setLoading(false);
        }
      } else {
        setSelectedWord('');
        setSynonyms([]);
      }
    };
    editor.on('selectionUpdate', handler);
    handler();
    return () => editor.off('selectionUpdate', handler);
  }, [editor, getSynonyms]);

  if (!editor || !selectedWord) return null;

  return (
    <BubbleMenu
      editor={editor}
      tippyOptions={{ duration: 100, placement: 'bottom' }}
      className="flex flex-col gap-2 rounded-lg border bg-popover p-2 shadow-md min-w-[180px]"
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-muted-foreground">{selectedWord}</span>
        <button
          type="button"
          onClick={() => onLookup?.(selectedWord)}
          className="flex items-center gap-1 text-xs text-primary hover:underline"
        >
          <BookOpen className="h-3 w-3" />
          Look up
        </button>
      </div>
      {loading ? (
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
      ) : synonyms.length > 0 ? (
        <div className="flex flex-wrap gap-1">
          {synonyms.slice(0, 8).map((s) => (
            <button
              key={s}
              type="button"
              onMouseDown={(e) => {
                e.preventDefault();
                const { from, to } = editor.state.selection;
                editor.chain().focus().setTextSelection({ from, to }).insertContent(s).run();
              }}
              className="rounded bg-muted px-2 py-0.5 text-xs hover:bg-primary/20 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      ) : (
        <span className="text-xs text-muted-foreground">No synonyms found</span>
      )}
    </BubbleMenu>
  );
}
