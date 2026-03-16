'use client';

import { useCallback, useMemo, useState } from 'react';
import type { Editor } from '@tiptap/react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Search, Replace, ChevronUp, FileText } from 'lucide-react';
import { replaceInTiptapJson, tiptapToPlainText } from '@/lib/tiptap-utils';

interface ChapterForSearch {
  id: string;
  title: string;
  content: Record<string, unknown>;
}

interface FindReplaceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editorRef: React.RefObject<Editor | null>;
  chapters?: ChapterForSearch[];
  activeChapterId?: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

export function FindReplaceDialog({
  open,
  onOpenChange,
  editorRef,
  chapters = [],
  activeChapterId,
  onSelectChapter,
}: FindReplaceDialogProps) {
  const editor = editorRef.current;
  const [find, setFind] = useState('');
  const [replace, setReplace] = useState('');
  const [scope, setScope] = useState<'chapter' | 'manuscript'>('chapter');

  const manuscriptMatches = useMemo(() => {
    if (!find.trim() || chapters.length === 0) return [];
    const lower = find.toLowerCase();
    const results: { chapterId: string; title: string; count: number }[] = [];
    for (const ch of chapters) {
      const text = tiptapToPlainText(ch.content as Record<string, unknown>);
      let count = 0;
      let idx = 0;
      while ((idx = text.toLowerCase().indexOf(lower, idx)) >= 0) {
        count++;
        idx += 1;
      }
      if (count > 0) results.push({ chapterId: ch.id, title: ch.title, count });
    }
    return results;
  }, [find, chapters]);

  const handleFind = useCallback((direction: 'next' | 'prev' = 'next') => {
    if (!editor || !find) return;
    if (!find) return;
    const lower = find.toLowerCase();
    const positions: number[] = [];
    editor.state.doc.descendants((node, offset) => {
      if (node.isText && node.text) {
        const nodeLower = node.text.toLowerCase();
        let idx = 0;
        while ((idx = nodeLower.indexOf(lower, idx)) >= 0) {
          positions.push(offset + idx);
          idx += 1;
        }
      }
      return true;
    });
    if (positions.length === 0) return;
    const { from } = editor.state.selection;
    let nextIdx: number;
    if (direction === 'next') {
      nextIdx = positions.findIndex((p) => p > from);
      if (nextIdx < 0) nextIdx = 0;
    } else {
      nextIdx = positions.findIndex((p) => p >= from) - 1;
      if (nextIdx < 0) nextIdx = positions.length - 1;
    }
    const start = positions[nextIdx];
    editor.commands.setTextSelection({ from: start, to: start + find.length });
    editor.commands.scrollIntoView();
  }, [editor, find]);

  const handleReplace = useCallback(() => {
    if (!editor || !find) return;
    const { from, to } = editor.state.selection;
    const selected = editor.state.doc.textBetween(from, to);
    if (selected.toLowerCase() === find.toLowerCase()) {
      editor.commands.insertContent(replace);
    }
  }, [editor, find, replace]);

  const handleReplaceAll = useCallback(() => {
    if (!editor || !find) return;
    const json = editor.getJSON();
    const updated = replaceInTiptapJson(json, find, replace, false);
    editor.commands.setContent(updated);
  }, [editor, find, replace]);

  const canSearchChapter = !!editor && scope === 'chapter';
  const showManuscriptResults = scope === 'manuscript' && find.trim().length > 0;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Find & Replace</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          {chapters.length > 1 && (
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setScope('chapter')}
                className={`rounded px-2 py-1 text-xs ${scope === 'chapter' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
              >
                Find in chapter
              </button>
              <button
                type="button"
                onClick={() => setScope('manuscript')}
                className={`rounded px-2 py-1 text-xs ${scope === 'manuscript' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}
              >
                Search manuscript
              </button>
            </div>
          )}
          <div className="grid gap-2">
            <Label htmlFor="find">Find</Label>
            <div className="flex gap-2">
              <Input
                id="find"
                value={find}
                onChange={(e) => setFind(e.target.value)}
                onKeyDown={(e) => canSearchChapter && e.key === 'Enter' && (e.shiftKey ? handleFind('prev') : handleFind('next'))}
                placeholder="Search..."
              />
              {canSearchChapter && (
                <>
                  <Button variant="outline" size="icon" onClick={() => handleFind('next')} title="Find next (Enter)">
                    <Search className="h-4 w-4" />
                  </Button>
                  <Button variant="outline" size="icon" onClick={() => handleFind('prev')} title="Find previous (Shift+Enter)">
                    <ChevronUp className="h-4 w-4" />
                  </Button>
                </>
              )}
            </div>
          </div>
          {showManuscriptResults && (
            <div className="rounded border p-2 max-h-32 overflow-auto">
              <p className="text-xs font-medium text-muted-foreground mb-1">Matches in manuscript</p>
              {manuscriptMatches.length === 0 ? (
                <p className="text-sm text-muted-foreground">No matches</p>
              ) : (
                <div className="space-y-1">
                  {manuscriptMatches.map(({ chapterId, title, count }) => (
                    <button
                      key={chapterId}
                      type="button"
                      onClick={() => {
                        onSelectChapter?.(chapterId);
                        onOpenChange(false);
                      }}
                      className={`flex w-full items-center gap-2 rounded px-2 py-1 text-left text-sm hover:bg-muted ${
                        chapterId === activeChapterId ? 'bg-primary/10' : ''
                      }`}
                    >
                      <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="truncate flex-1">{title}</span>
                      <span className="text-xs text-muted-foreground">{count}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
          <div className="grid gap-2">
            <Label htmlFor="replace">Replace with</Label>
            <div className="flex gap-2">
              <Input
                id="replace"
                value={replace}
                onChange={(e) => setReplace(e.target.value)}
                placeholder="Replace with..."
              />
              {canSearchChapter && (
                <>
                  <Button variant="outline" onClick={handleReplace}>
                    <Replace className="h-4 w-4 mr-1" />
                    Replace
                  </Button>
                  <Button variant="outline" onClick={handleReplaceAll}>
                    Replace all
                  </Button>
                </>
              )}
            </div>
          </div>
          {scope === 'manuscript' && (
            <p className="text-xs text-muted-foreground">
              Replace carefully. Switch to a chapter above to replace there.
            </p>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
