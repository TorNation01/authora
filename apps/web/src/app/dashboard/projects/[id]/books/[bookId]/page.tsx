'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { WritingStudioEditor } from '@/components/editor/WritingStudioEditor';
import { EditorReferenceContextMenu } from '@/components/editor/EditorReferenceContextMenu';
import { ManuscriptSidebar } from '@/components/studio/ManuscriptSidebar';
import { EditorToolbar } from '@/components/studio/EditorToolbar';
import { AIWritingPanel } from '@/components/studio/AIWritingPanel';
import { NotesPanel } from '@/components/studio/NotesPanel';
import { ReferencePanel } from '@/components/studio/ReferencePanel';
import { FindReplaceDialog } from '@/components/studio/FindReplaceDialog';
import { VersionHistoryDialog } from '@/components/studio/VersionHistoryDialog';
import { QuickInsertDialog } from '@/components/studio/QuickInsertDialog';
import { api, apiStream } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useAutosave } from '@/hooks/useAutosave';
import { cn } from '@/lib/utils';
import { tiptapToPlainText, replaceInTiptapJson } from '@/lib/tiptap-utils';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  content: Record<string, unknown>;
  word_count: number;
  section_status?: string | null;
}

interface Book {
  id: string;
  title: string;
  type?: string;
  chapters: Chapter[];
}

interface Version {
  id: string;
  chapter_id: string;
  content: Record<string, unknown>;
  word_count: number;
  created_at: string;
}

type PanelMode = 'none' | 'ai' | 'notes' | 'reference';

export default function BookStudioPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const [book, setBook] = useState<Book | null>(null);
  const [activeChapter, setActiveChapter] = useState<Chapter | null>(null);
  const [panelMode, setPanelMode] = useState<PanelMode>('none');
  const [distractionFree, setDistractionFree] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showFindReplace, setShowFindReplace] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showQuickInsert, setShowQuickInsert] = useState(false);
  const [versions, setVersions] = useState<Version[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [editorSelection, setEditorSelection] = useState('');
  const [lookupWord, setLookupWord] = useState<string | null>(null);
  const [activeReferenceTab, setActiveReferenceTab] = useState<'lookup' | 'analysis'>('lookup');
  const editorRef = useRef<import('@tiptap/react').Editor | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    api<Book>(`/api/v1/projects/${projectId}/books/${bookId}`)
      .then((b) => {
        setBook(b);
        if (b.chapters.length > 0 && !activeChapter) {
          setActiveChapter(b.chapters[0]);
        }
      })
      .catch(() => router.push('/dashboard'));
  }, [projectId, bookId, router]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  const saveChapter = useCallback(
    async (data: { content: Record<string, unknown>; wordCount: number }) => {
      if (!activeChapter) throw new Error('No chapter');
      await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ content: data.content }),
      });
      setActiveChapter((prev) =>
        prev ? { ...prev, content: data.content, word_count: data.wordCount } : null
      );
      if (book) {
        setBook({
          ...book,
          chapters: book.chapters.map((c) =>
            c.id === activeChapter.id ? { ...c, content: data.content, word_count: data.wordCount } : c
          ),
        });
      }
    },
    [activeChapter, book, projectId, bookId]
  );

  const { scheduleSave, status, flushPending } = useAutosave<{
    content: Record<string, unknown>;
    wordCount: number;
  }>({
    onSave: saveChapter,
    delayMs: 2000,
    onError: () => toast({ title: 'Failed to save', variant: 'destructive' }),
    maxRetries: 3,
  });

  const handleChapterChange = useCallback(
    (content: Record<string, unknown>, wordCount: number) => {
      if (!activeChapter) return;
      scheduleSave({ content, wordCount });
    },
    [activeChapter, scheduleSave]
  );

  const handleExport = useCallback(
    async (format: string) => {
      try {
        const token = localStorage.getItem('access_token');
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${bookId}/${format}`,
          { headers: token ? { Authorization: `Bearer ${token}` } : {} }
        );
        if (!res.ok) throw new Error('Export failed');
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${book?.title || 'book'}.${format}`;
        a.click();
        URL.revokeObjectURL(url);
        toast({ title: 'Export started' });
      } catch {
        toast({ title: 'Export failed', variant: 'destructive' });
      }
    },
    [bookId, book?.title, toast]
  );

  const handleSelectChapter = useCallback(
    async (ch: Chapter) => {
      await flushPending();
      setActiveChapter(ch);
    },
    [flushPending]
  );

  const handleReorder = useCallback(
    async (chapterIds: string[]) => {
      try {
        const updated = await api<Chapter[]>(
          `/api/v1/projects/${projectId}/books/${bookId}/chapters/reorder`,
          {
            method: 'POST',
            body: JSON.stringify({ chapter_ids: chapterIds }),
          }
        );
        if (book) setBook({ ...book, chapters: updated });
      } catch {
        toast({ title: 'Failed to reorder', variant: 'destructive' });
      }
    },
    [projectId, bookId, book, toast]
  );

  const handleAddChapter = useCallback(async () => {
    try {
      const ch = await api<Chapter>(`/api/v1/projects/${projectId}/books/${bookId}/chapters`, {
        method: 'POST',
        body: JSON.stringify({
          title: `Chapter ${(book?.chapters.length ?? 0) + 1}`,
          sort_order: book?.chapters.length ?? 0,
          content: { type: 'doc', content: [{ type: 'paragraph' }] },
        }),
      });
      setBook((b) => (b ? { ...b, chapters: [...b.chapters, ch] } : null));
      setActiveChapter(ch);
      toast({ title: 'Chapter added' });
    } catch {
      toast({ title: 'Failed to add chapter', variant: 'destructive' });
    }
  }, [projectId, bookId, book?.chapters.length, toast]);

  const handleStatusChange = useCallback(
    async (status: 'draft' | 'revising' | 'review' | 'done') => {
      if (!activeChapter) return;
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}`, {
          method: 'PATCH',
          body: JSON.stringify({ section_status: status }),
        });
        setActiveChapter((prev) => (prev ? { ...prev, section_status: status } : null));
        if (book) {
          setBook({
            ...book,
            chapters: book.chapters.map((c) =>
              c.id === activeChapter.id ? { ...c, section_status: status } : c
            ),
          });
        }
      } catch {
        toast({ title: 'Failed to update status', variant: 'destructive' });
      }
    },
    [activeChapter, book, projectId, bookId, toast]
  );

  const handleRestoreVersion = useCallback(
    async (version: Version) => {
      if (!activeChapter || version.chapter_id !== activeChapter.id) return;
      setActiveChapter((prev) => (prev ? { ...prev, content: version.content, word_count: version.word_count } : null));
      if (book) {
        setBook({
          ...book,
          chapters: book.chapters.map((c) =>
            c.id === activeChapter.id ? { ...c, content: version.content, word_count: version.word_count } : c
          ),
        });
      }
      await saveChapter({ content: version.content, wordCount: version.word_count });
      setShowHistory(false);
      toast({ title: 'Version restored' });
    },
    [activeChapter, book, saveChapter, toast]
  );

  const loadVersions = useCallback(async () => {
    if (!activeChapter) return;
    setVersionsLoading(true);
    try {
      const v = await api<Version[]>(
        `/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}/versions`
      );
      setVersions(v);
    } finally {
      setVersionsLoading(false);
    }
  }, [projectId, bookId, activeChapter?.id]);

  useEffect(() => {
    if (showHistory && activeChapter) loadVersions();
  }, [showHistory, activeChapter?.id, loadVersions]);

  const totalWords = book?.chapters.reduce((s, c) => s + c.word_count, 0) ?? 0;
  const sortedChapters = [...(book?.chapters ?? [])].sort((a, b) => a.sort_order - b.sort_order);

  const documentText =
    activeChapter?.content && typeof activeChapter.content === 'object'
      ? tiptapToPlainText(activeChapter.content as Record<string, unknown>)
      : '';

  const handleLookup = useCallback((word: string) => {
    setLookupWord(word);
    setPanelMode('reference');
    setActiveReferenceTab('lookup');
  }, []);

  const handleReplace = useCallback((from: string, to: string) => {
    if (!editorRef.current) return;
    const content = editorRef.current.getJSON();
    const updated = replaceInTiptapJson(content, from, to);
    editorRef.current.commands.setContent(updated);
  }, []);

  const handleWordSelect = useCallback((word: string) => {
    setLookupWord(word);
    setActiveReferenceTab('lookup');
  }, []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        const sel = editorSelection.trim().split(/\s+/);
        if (sel.length === 1 && /^[a-zA-Z']+$/.test(sel[0])) {
          handleLookup(sel[0]);
        }
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [editorSelection, handleLookup]);

  return (
    <div className={cn('flex h-[calc(100vh-0px)]', darkMode && 'dark')}>
      {!distractionFree && (
        <ManuscriptSidebar
          bookTitle={book?.title ?? 'Book'}
          bookType={book?.type}
          projectId={projectId}
          bookId={bookId}
          chapters={sortedChapters}
          activeChapterId={activeChapter?.id ?? null}
          onSelectChapter={handleSelectChapter}
          onReorder={handleReorder}
          onAddChapter={handleAddChapter}
        />
      )}

      <div className="flex flex-1 flex-col min-w-0">
        {!distractionFree && (
          <EditorToolbar
            chapterTitle={activeChapter?.title ?? 'Select a chapter'}
            chapterWordCount={activeChapter?.word_count ?? 0}
            totalWordCount={totalWords}
            saveStatus={status}
            distractionFree={distractionFree}
            darkMode={darkMode}
            panelMode={panelMode}
            onToggleDistractionFree={() => setDistractionFree(true)}
            onToggleDarkMode={() => setDarkMode((d) => !d)}
            onTogglePanel={setPanelMode}
            onExport={handleExport}
            onHistory={() => setShowHistory(true)}
            onFindReplace={() => setShowFindReplace(true)}
            onQuickInsert={() => setShowQuickInsert(true)}
            onStatusChange={handleStatusChange}
            sectionStatus={activeChapter?.section_status}
            showAi={!!book?.type}
          />
        )}

        {distractionFree && (
          <div className="flex items-center justify-between border-b px-4 py-2">
            <span className="text-sm text-muted-foreground">Focus mode</span>
            <button
              type="button"
              className="text-sm text-primary hover:underline"
              onClick={() => setDistractionFree(false)}
            >
              Exit
            </button>
          </div>
        )}

        <div className="flex flex-1 min-h-0">
          <div className={cn('flex-1 overflow-auto', distractionFree ? 'p-8 max-w-3xl mx-auto' : 'p-6')}>
            {activeChapter ? (
              <EditorReferenceContextMenu selection={editorSelection} onLookup={handleLookup}>
                <WritingStudioEditor
                content={activeChapter.content}
                onChange={handleChapterChange}
                placeholder="Start writing your chapter..."
                distractionFree={distractionFree}
                editorRef={editorRef}
                onSelectionChange={setEditorSelection}
                onLookup={handleLookup}
              />
              </EditorReferenceContextMenu>
            ) : (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                Select a chapter or add one to start writing
              </div>
            )}
          </div>

          {panelMode === 'ai' && book && (
            <AIWritingPanel
              projectId={projectId}
              bookId={bookId}
              bookType={book.type === 'fiction' ? 'fiction' : book.type === 'nonfiction' ? 'nonfiction' : undefined}
              chapterId={activeChapter?.id}
              selection={editorSelection}
              isFiction={book.type === 'fiction'}
              isNonfiction={book.type === 'nonfiction'}
              onInsert={(text) => {
                if (editorRef.current) editorRef.current.commands.insertContent(text);
              }}
              onComplete={async (prompt, onChunk) => {
                try {
                  await apiStream('/api/v1/ai/complete', onChunk, {
                    method: 'POST',
                    body: JSON.stringify({
                      prompt,
                      chapter_id: activeChapter?.id,
                      book_id: bookId,
                    }),
                  });
                } catch (err) {
                  toast({
                    title: 'AI error',
                    description: err instanceof Error ? err.message : 'AI not configured',
                    variant: 'destructive',
                  });
                }
              }}
              onNonfictionPrompt={
                book.type === 'nonfiction'
                  ? async (promptType, onChunk, selection) => {
                      try {
                        const token = localStorage.getItem('access_token');
                        const res = await fetch(
                          `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/projects/${projectId}/books/${bookId}/nonfiction/ai`,
                          {
                            method: 'POST',
                            headers: {
                              'Content-Type': 'application/json',
                              ...(token ? { Authorization: `Bearer ${token}` } : {}),
                            },
                            body: JSON.stringify({
                              prompt_type: promptType,
                              chapter_id: activeChapter?.id,
                              selection: selection || null,
                            }),
                          }
                        );
                        if (!res.ok) throw new Error(await res.text());
                        const reader = res.body?.getReader();
                        if (!reader) return;
                        const decoder = new TextDecoder();
                        while (true) {
                          const { done, value } = await reader.read();
                          if (done) break;
                          onChunk(decoder.decode(value, { stream: true }));
                        }
                      } catch (err) {
                        toast({
                          title: 'AI error',
                          description: err instanceof Error ? err.message : 'AI not configured',
                          variant: 'destructive',
                        });
                      }
                    }
                  : undefined
              }
              onFictionPrompt={
                book.type === 'fiction'
                  ? async (promptType, onChunk, selection) => {
                      try {
                        const token = localStorage.getItem('access_token');
                        const res = await fetch(
                          `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/projects/${projectId}/books/${bookId}/fiction/ai`,
                          {
                            method: 'POST',
                            headers: {
                              'Content-Type': 'application/json',
                              ...(token ? { Authorization: `Bearer ${token}` } : {}),
                            },
                            body: JSON.stringify({
                              prompt_type: promptType,
                              chapter_id: activeChapter?.id,
                              selection: selection || null,
                            }),
                          }
                        );
                        if (!res.ok) throw new Error(await res.text());
                        const reader = res.body?.getReader();
                        if (!reader) return;
                        const decoder = new TextDecoder();
                        while (true) {
                          const { done, value } = await reader.read();
                          if (done) break;
                          onChunk(decoder.decode(value, { stream: true }));
                        }
                      } catch (err) {
                        toast({
                          title: 'AI error',
                          description: err instanceof Error ? err.message : 'AI not configured',
                          variant: 'destructive',
                        });
                      }
                    }
                  : undefined
              }
            />
          )}

          {panelMode === 'notes' && (
            <NotesPanel
              projectId={projectId}
              bookId={bookId}
              activeChapterId={activeChapter?.id ?? null}
            />
          )}

          {panelMode === 'reference' && (
            <ReferencePanel
              lookupWord={lookupWord}
              documentText={documentText}
              onWordSelect={handleWordSelect}
              onReplace={handleReplace}
              activeTab={activeReferenceTab}
              onActiveTabChange={setActiveReferenceTab}
            />
          )}
        </div>
      </div>

      <FindReplaceDialog
        open={showFindReplace}
        onOpenChange={setShowFindReplace}
        editorRef={editorRef}
      />
      <VersionHistoryDialog
        open={showHistory}
        onOpenChange={setShowHistory}
        versions={versions}
        loading={versionsLoading}
        onRestore={handleRestoreVersion}
      />
      <QuickInsertDialog
        open={showQuickInsert}
        onOpenChange={setShowQuickInsert}
        editorRef={editorRef}
      />
    </div>
  );
}
