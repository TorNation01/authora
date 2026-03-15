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
import { Search, Replace } from 'lucide-react';
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

  const handleFind = () => {
    if (!find) return;
    const text = editor.getText();
    const idx = text.toLowerCase().indexOf(find.toLowerCase());
    if (idx < 0) return;
    let pos = 0;
    editor.state.doc.descendants((node, offset) => {
      const len = node.textContent.length;
      if (pos + len > idx) {
        const start = offset;
        const end = Math.min(offset + find.length, offset + len);
        editor.commands.setTextSelection({ from: start, to: end });
        return false;
      }
      pos += len;
    });
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
                placeholder="Search..."
              />
              <Button variant="outline" size="icon" onClick={handleFind}>
                <Search className="h-4 w-4" />
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
