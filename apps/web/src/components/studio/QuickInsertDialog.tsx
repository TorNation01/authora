'use client';

import type { Editor } from '@tiptap/react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

const TEMPLATES: Array<{ label: string; insert: string | Record<string, unknown> }> = [
  { label: 'Scene break', insert: '\n\n***\n\n' },
  {
    label: 'Chapter heading',
    insert: { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: 'Chapter Title' }] },
  },
  {
    label: 'Subheading',
    insert: { type: 'heading', attrs: { level: 3 }, content: [{ type: 'text', text: 'Subheading' }] },
  },
  {
    label: 'Blockquote',
    insert: {
      type: 'blockquote',
      content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Quote...' }] }],
    },
  },
  {
    label: 'Bullet list',
    insert: {
      type: 'bulletList',
      content: [
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Item 1' }] }] },
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Item 2' }] }] },
      ],
    },
  },
  {
    label: 'Numbered list',
    insert: {
      type: 'orderedList',
      content: [
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'First' }] }] },
        { type: 'listItem', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Second' }] }] },
      ],
    },
  },
];

interface QuickInsertDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  editorRef: React.RefObject<Editor | null>;
}

export function QuickInsertDialog({ open, onOpenChange, editorRef }: QuickInsertDialogProps) {
  const editor = editorRef.current;
  if (!editor) return null;

  const handleInsert = (item: string | Record<string, unknown>) => {
    editor.commands.insertContent(item);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Quick insert</DialogTitle>
        </DialogHeader>
        <div className="grid gap-2">
          {TEMPLATES.map((t) => (
            <Button
              key={t.label}
              variant="outline"
              className="justify-start"
              onClick={() => handleInsert(t.insert)}
            >
              {t.label}
            </Button>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
