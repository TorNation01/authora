'use client';

import { useCallback, useEffect, useState } from 'react';
import type { Editor } from '@tiptap/react';
import { BookOpen, MessageSquarePlus } from 'lucide-react';

interface EditorReferenceContextMenuProps {
  children: React.ReactNode;
  selection: string;
  onLookup: (word: string) => void;
  onAddComment?: (startOffset: number, endOffset: number, body: string) => void;
  editorRef?: React.RefObject<Editor | null>;
}

export function EditorReferenceContextMenu({
  children,
  selection,
  onLookup,
  onAddComment,
  editorRef,
}: EditorReferenceContextMenuProps) {
  const [menu, setMenu] = useState<{ x: number; y: number; word: string; hasSelection: boolean } | null>(null);
  const [commentDialog, setCommentDialog] = useState<{ startOffset: number; endOffset: number } | null>(null);
  const [commentBody, setCommentBody] = useState('');

  const handleContextMenu = useCallback(
    (e: React.MouseEvent) => {
      const text = selection.trim();
      if (!text) return;
      const words = text.split(/\s+/);
      const singleWord = words.length === 1 && /^[a-zA-Z']+$/.test(words[0]);
      if (singleWord || (onAddComment && text.length > 0)) {
        e.preventDefault();
        setMenu({ x: e.clientX, y: e.clientY, word: singleWord ? words[0] : '', hasSelection: text.length > 0 });
      }
    },
    [selection, onAddComment]
  );

  const handleAddComment = useCallback(() => {
    setMenu(null);
    if (!onAddComment || !editorRef?.current) return;
    const editor = editorRef.current;
    const { from, to } = editor.state.selection;
    const startOffset = editor.state.doc.textBetween(0, from).length;
    const endOffset = startOffset + editor.state.doc.textBetween(from, to).length;
    setCommentBody('');
    setCommentDialog({ startOffset, endOffset });
  }, [onAddComment, editorRef]);

  const submitComment = useCallback(() => {
    if (!commentDialog || !commentBody.trim()) return;
    onAddComment?.(commentDialog.startOffset, commentDialog.endOffset, commentBody.trim());
    setCommentDialog(null);
    setCommentBody('');
  }, [commentDialog, commentBody, onAddComment]);

  useEffect(() => {
    if (!menu) return;
    const close = () => setMenu(null);
    window.addEventListener('click', close);
    window.addEventListener('scroll', close, true);
    return () => {
      window.removeEventListener('click', close);
      window.removeEventListener('scroll', close, true);
    };
  }, [menu]);

  return (
    <>
      <div onContextMenu={handleContextMenu} className="contents">
        {children}
      </div>
      {menu && (
        <div
          className="fixed z-[99989] min-w-[160px] rounded-lg border bg-popover py-1 shadow-md"
          style={{ left: menu.x, top: menu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          {menu.word && (
            <button
              type="button"
              className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
              onClick={() => {
                onLookup(menu.word);
                setMenu(null);
              }}
            >
              <BookOpen className="h-4 w-4" />
              Look up &quot;{menu.word}&quot;
            </button>
          )}
          {onAddComment && menu.hasSelection && (
            <button
              type="button"
              className="flex w-full items-center gap-2 px-3 py-2 text-sm hover:bg-accent"
              onClick={handleAddComment}
            >
              <MessageSquarePlus className="h-4 w-4" />
              Add comment
            </button>
          )}
        </div>
      )}
      {commentDialog && (
        <div
          className="fixed inset-0 z-[99990] flex items-center justify-center bg-black/20"
          onClick={() => setCommentDialog(null)}
        >
          <div
            className="rounded-lg border bg-background p-4 shadow-lg min-w-[320px]"
            onClick={(e) => e.stopPropagation()}
          >
            <p className="text-sm font-medium mb-2">Add comment</p>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm min-h-[80px]"
              placeholder="Leave yourself a marker…"
              value={commentBody}
              onChange={(e) => setCommentBody(e.target.value)}
              autoFocus
            />
            <div className="flex justify-end gap-2 mt-3">
              <button
                type="button"
                className="rounded px-3 py-1 text-sm border"
                onClick={() => setCommentDialog(null)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="rounded px-3 py-1 text-sm bg-primary text-primary-foreground"
                onClick={submitComment}
                disabled={!commentBody.trim()}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
