'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Typography from '@tiptap/extension-typography';
import { useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface EditorProps {
  content: Record<string, unknown>;
  onChange: (content: Record<string, unknown>, wordCount: number) => void;
  placeholder?: string;
  className?: string;
}

function countWords(doc: { content?: Array<{ content?: Array<{ text?: string }>; text?: string }> }): number {
  let text = '';
  const walk = (node: unknown) => {
    if (node && typeof node === 'object') {
      const n = node as Record<string, unknown>;
      if ('text' in n && typeof n.text === 'string') text += n.text + ' ';
      if ('content' in n && Array.isArray(n.content)) n.content.forEach(walk);
    }
  };
  if (doc?.content) doc.content.forEach(walk);
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export function Editor({ content, onChange, placeholder = 'Start writing...', className }: EditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder }),
      Typography,
    ],
    content: content?.content ? content : { type: 'doc', content: [{ type: 'paragraph' }] },
    editorProps: {
      attributes: {
        class: 'prose prose-lg max-w-none font-serif focus:outline-none min-h-[400px]',
      },
    },
    onUpdate: ({ editor }) => {
      const json = editor.getJSON();
      onChange(json, countWords(json));
    },
  });

  useEffect(() => {
    if (editor && content && JSON.stringify(editor.getJSON()) !== JSON.stringify(content)) {
      editor.commands.setContent(content?.content ? content : { type: 'doc', content: [{ type: 'paragraph' }] });
    }
  }, [content, editor]);

  return (
    <div className={cn('border rounded-lg bg-background', className)}>
      <EditorContent editor={editor} />
    </div>
  );
}
