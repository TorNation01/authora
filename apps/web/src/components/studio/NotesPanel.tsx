'use client';

import { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import { StickyNote, Plus, Loader2, Pin, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface Note {
  id: string;
  title: string;
  content: string;
  note_type: string;
  pinned: boolean;
  is_inspiration: boolean;
  chapter_id: string | null;
  tags: string[];
}

interface NotesPanelProps {
  projectId?: string;
  bookId?: string;
  activeChapterId?: string | null;
  className?: string;
}

export function NotesPanel({
  projectId,
  bookId,
  activeChapterId,
  className,
}: NotesPanelProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [quickAdd, setQuickAdd] = useState('');

  const fetchNotes = useCallback(() => {
    if (!projectId) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (bookId) params.set('book_id', bookId);
    if (activeChapterId) params.set('chapter_id', activeChapterId);
    api<Note[]>(`/api/v1/projects/${projectId}/notes${params.toString() ? `?${params}` : ''}`)
      .then(setNotes)
      .catch(() => setNotes([]))
      .finally(() => setLoading(false));
  }, [projectId, bookId, activeChapterId]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleAdd = async () => {
    if (!quickAdd.trim() || !projectId) return;
    try {
      await api(`/api/v1/projects/${projectId}/notes`, {
        method: 'POST',
        body: JSON.stringify({
          title: quickAdd.slice(0, 80) + (quickAdd.length > 80 ? '...' : ''),
          content: quickAdd,
          note_type: 'general',
          book_id: bookId || null,
          chapter_id: activeChapterId || null,
        }),
      });
      setQuickAdd('');
      fetchNotes();
    } catch {
      /* ignore */
    }
  };

  const notesLink = projectId ? `/dashboard/projects/${projectId}/notes` : '/dashboard/notes';

  return (
    <div className={cn('flex flex-col border-l bg-card w-80', className)}>
      <div className="flex items-center justify-between border-b p-3">
        <h3 className="font-medium flex items-center gap-2">
          <StickyNote className="h-4 w-4" />
          Notes
        </h3>
        <Link href={notesLink}>
          <Button variant="ghost" size="sm">
            Open all
          </Button>
        </Link>
      </div>
      <div className="flex-1 overflow-auto p-3 space-y-3">
        {projectId && (
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Quick note..."
              value={quickAdd}
              onChange={(e) => setQuickAdd(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
              className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
            <Button variant="ghost" size="sm" onClick={handleAdd} disabled={!quickAdd.trim()}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        )}
        {loading ? (
          <div className="flex justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : notes.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            {projectId
              ? 'No notes yet. Add one above or open the full notes page.'
              : 'Notes live with your projects. Open a book to add notes.'}
          </p>
        ) : (
          notes.map((note) => (
            <div
              key={note.id}
              className="rounded-lg border bg-muted/30 dark:bg-muted/10 p-3 min-h-[60px]"
            >
              <div className="flex items-start gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm truncate">{note.title}</p>
                  <p className="text-sm text-muted-foreground line-clamp-2 mt-0.5">{note.content}</p>
                </div>
                <div className="flex gap-0.5 shrink-0">
                  {note.pinned && <Pin className="h-3 w-3 text-muted-foreground" />}
                  {note.is_inspiration && <Sparkles className="h-3 w-3 text-amber-500" />}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
