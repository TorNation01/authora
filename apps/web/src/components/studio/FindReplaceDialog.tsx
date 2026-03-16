'use client';

import { useState } from 'react';
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
import { Search, Replace, ChevronDown, ChevronUp } from 'lucide-react';
import { replaceInTiptapJson } from '@/lib/tiptap-utils';

interface FindReplaceDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editorRef: React.RefObject<Editor | null>;
}

export function FindReplaceDialog({ open, onOpenChange, editorRef }: FindReplaceDialogProps) {
  const editor = editorRef.current;
  const [find, setFind] = useState('');
  const [replace, setReplace] = useState('');

  if (!editor) return null;

  const handleFind = (direction: 'next' | 'prev' = 'next') => {
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
  };

  const handleReplace = () => {
    if (!find) return;
    const { from, to } = editor.state.selection;
    const selected = editor.state.doc.textBetween(from, to);
    if (selected.toLowerCase() === find.toLowerCase()) {
      editor.commands.insertContent(replace);
    }
  };

  const handleReplaceAll = () => {
    if (!find) return;
    const json = editor.getJSON();
    const updated = replaceInTiptapJson(json, find, replace, false);
    editor.commands.setContent(updated);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Find & Replace</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="find">Find</Label>
            <div className="flex gap-2">
              <Input
                id="find"
                value={find}
                onChange={(e) => setFind(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && (e.shiftKey ? handleFind('prev') : handleFind('next'))}
                placeholder="Search..."
              />
              <Button variant="outline" size="icon" onClick={() => handleFind('next')} title="Find next (Enter)">
                <Search className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="icon" onClick={() => handleFind('prev')} title="Find previous (Shift+Enter)">
                <ChevronUp className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="replace">Replace with</Label>
            <div className="flex gap-2">
              <Input
                id="replace"
                value={replace}
                onChange={(e) => setReplace(e.target.value)}
                placeholder="Replace with..."
              />
              <Button variant="outline" onClick={handleReplace}>
                <Replace className="h-4 w-4 mr-1" />
                Replace
              </Button>
              <Button variant="outline" onClick={handleReplaceAll}>
                Replace all
              </Button>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
