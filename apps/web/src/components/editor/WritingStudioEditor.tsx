'use client';

import type { Editor } from '@tiptap/react';
import { useEditor, EditorContent } from '@tiptap/react';
import { useEffect } from 'react';
import { cn } from '@/lib/utils';
import { editorExtensions } from './extensions';
import { EditorBubbleMenu } from './EditorBubbleMenu';
import { ReferenceBubbleMenu } from './ReferenceBubbleMenu';

interface WritingStudioEditorProps {
  content: Record<string, unknown>;
  onChange: (content: Record<string, unknown>, wordCount: number) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
  distractionFree?: boolean;
  editorRef?: React.MutableRefObject<Editor | null>;
  onSelectionChange?: (text: string) => void;
  onLookup?: (word: string) => void;
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

const emptyDoc = { type: 'doc', content: [{ type: 'paragraph' }] };

export function WritingStudioEditor({
  content,
  onChange,
  placeholder = 'Start writing...',
  className,
  disabled,
  distractionFree,
  editorRef,
  onSelectionChange,
  onLookup,
}: WritingStudioEditorProps) {
  const editor = useEditor({
    extensions: editorExtensions(placeholder),
    content: content?.content ? content : emptyDoc,
    editable: !disabled,
    editorProps: {
      attributes: {
        class: cn(
          'prose prose-lg max-w-none font-serif focus:outline-none min-h-[400px]',
          distractionFree && 'prose-sanctuary'
        ),
      },
    },
    onUpdate: ({ editor }) => {
      const json = editor.getJSON();
      onChange(json, countWords(json));
    },
  });

  useEffect(() => {
    if (editor && content && JSON.stringify(editor.getJSON()) !== JSON.stringify(content)) {
      editor.commands.setContent(content?.content ? content : emptyDoc);
    }
  }, [content, editor]);

  useEffect(() => {
    if (editor) editor.setEditable(!disabled);
  }, [disabled, editor]);

  useEffect(() => {
    if (editorRef) editorRef.current = editor;
    return () => {
      if (editorRef) editorRef.current = null;
    };
  }, [editor, editorRef]);

  useEffect(() => {
    if (!editor || !onSelectionChange) return;
    const handler = () => {
      const { from, to } = editor.state.selection;
      const text = editor.state.doc.textBetween(from, to);
      onSelectionChange(text);
    };
    editor.on('selectionUpdate', handler);
    handler();
    return () => editor.off('selectionUpdate', handler);
  }, [editor, onSelectionChange]);

  return (
    <div className={cn('relative rounded-lg bg-background', !distractionFree && 'border', className)}>
      <EditorBubbleMenu editor={editor} />
      <ReferenceBubbleMenu editor={editor} onLookup={onLookup} />
      <EditorContent editor={editor} />
    </div>
  );
}
