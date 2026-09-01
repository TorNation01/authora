'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { WritingStudioEditor } from '@/components/editor/WritingStudioEditor';
import { EditorReferenceContextMenu } from '@/components/editor/EditorReferenceContextMenu';
import { ManuscriptSidebar } from '@/components/studio/ManuscriptSidebar';
import { EditorToolbar } from '@/components/studio/EditorToolbar';
import { FinishModeSidebar } from '@/components/studio/FinishModeSidebar';
import { FinishModePanel, type FinishModeStats } from '@/components/studio/FinishModePanel';
import { FinishModeSettingsDialog } from '@/components/studio/FinishModeSettingsDialog';
import { FinishModeCompletionCeremony } from '@/components/studio/FinishModeCompletionCeremony';
import { RecoveryBanner } from '@/components/studio/RecoveryBanner';
import { AIWritingPanel } from '@/components/studio/AIWritingPanel';
import { NotesPanel } from '@/components/studio/NotesPanel';
import { VaultKnowledgePanel } from '@/components/vault/VaultKnowledgePanel';
import { ReferencePanel } from '@/components/studio/ReferencePanel';
import { FindReplaceDialog } from '@/components/studio/FindReplaceDialog';
import { RevisionPanel } from '@/components/studio/RevisionPanel';
import { VersionHistoryDialog } from '@/components/studio/VersionHistoryDialog';
import { RecoveryCenterDialog } from '@/components/studio/RecoveryCenterDialog';
import { QuickInsertDialog } from '@/components/studio/QuickInsertDialog';
import { ImportDocumentDialog } from '@/components/studio/ImportDocumentDialog';
import { StoryIntegrityPanel } from '@/components/studio/StoryIntegrityPanel';
import { FirstWritePromptBlock, hasCompletedFirstWrite, markFirstWriteDone } from '@/components/studio/FirstWritePromptBlock';
import { FirstWriteProgress } from '@/components/studio/FirstWriteProgress';
import { GuidedOverlay } from '@/components/tutorial/GuidedOverlay';
import { useConfig } from '@/contexts/ConfigProvider';
import { useTutorial } from '@/contexts/TutorialContext';
import { useWriterStudioPreferences } from '@/hooks/useWriterStudioPreferences';
import { Button } from '@/components/ui/button';
import { api, apiStream, ApiError } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useAutosave } from '@/hooks/useAutosave';
import { useUnsavedChangesGuard } from '@/hooks/useUnsavedChangesGuard';
import { loadDraft, clearDraft, isStorageAvailable } from '@/lib/draft-storage';
import { cn } from '@/lib/utils';
import { tiptapToPlainText, replaceInTiptapJson } from '@/lib/tiptap-utils';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  content: Record<string, unknown>;
  word_count: number;
  section_status?: string | null;
  section_group?: string | null;
  tags?: string[];
  updated_at?: string;
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

type PanelMode = 'none' | 'ai' | 'notes' | 'reference' | 'revision' | 'vault' | 'integrity';

export default function BookStudioPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const [book, setBook] = useState<Book | null>(null);
  const [activeChapter, setActiveChapter] = useState<Chapter | null>(null);
  const [panelMode, setPanelMode] = useState<PanelMode>('none');
  const [distractionFree, setDistractionFree] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [showFindReplace, setShowFindReplace] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showRecoveryCenter, setShowRecoveryCenter] = useState(false);
  const [showQuickInsert, setShowQuickInsert] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [versions, setVersions] = useState<Version[]>([]);
  const [versionsLoading, setVersionsLoading] = useState(false);
  const [editorSelection, setEditorSelection] = useState('');
  const [lookupWord, setLookupWord] = useState<string | null>(null);
  const [activeReferenceTab, setActiveReferenceTab] = useState<'lookup' | 'analysis'>('lookup');
  const [finishModeStats, setFinishModeStats] = useState<FinishModeStats | null>(null);
  const [showFinishModeSettings, setShowFinishModeSettings] = useState(false);
  const [liveWordCount, setLiveWordCount] = useState<number | null>(null);
  const [generatingStarter, setGeneratingStarter] = useState(false);
  const editorRef = useRef<import('@tiptap/react').Editor | null>(null);
  const { toast } = useToast();
  const config = useConfig();
  const { shouldShowOverlay, markCompleted, markDismissed } = useTutorial();
  const storyIntegrityEnabled = config.feature_flags?.story_integrity ?? true;
  const storyDensityEnabled = config.feature_flags?.story_density ?? true;
  const {
    sidebarPosition,
    sidebarCollapsed,
    toggleSidebar,
    setSidebarPosition,
  } = useWriterStudioPreferences();

  const fetchFinishMode = useCallback(() => {
    api<FinishModeStats>(`/api/v1/projects/${projectId}/books/${bookId}/finish-mode`)
      .then(setFinishModeStats)
      .catch(() => setFinishModeStats(null));
  }, [projectId, bookId]);

  useEffect(() => {
    api<Book>(`/api/v1/projects/${projectId}/books/${bookId}`)
      .then((b) => {
        setBook(b);
        if (b.chapters.length > 0) {
          const chapterId = searchParams.get('chapter');
          const target =
            chapterId && b.chapters.some((c) => c.id === chapterId)
              ? b.chapters.find((c) => c.id === chapterId)!
              : b.chapters[0];
          setActiveChapter(target);
        }
      })
      .catch(() => router.push('/dashboard'));
  }, [projectId, bookId, router]);

  useEffect(() => {
    if (bookId) fetchFinishMode();
  }, [bookId, fetchFinishMode]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
  }, [darkMode]);

  useEffect(() => {
    if (activeChapter?.id && book?.id) {
      api('/api/v1/projects/resume-session', {
        method: 'POST',
        body: JSON.stringify({
          project_id: projectId,
          book_id: bookId,
          chapter_id: activeChapter.id,
        }),
      }).catch(() => {});
    }
  }, [projectId, bookId, activeChapter?.id, book?.id]);

  const saveChapter = useCallback(
    async (data: { content: Record<string, unknown>; wordCount: number }) => {
      if (!activeChapter) throw new Error('No chapter');
      const body: Record<string, unknown> = { content: data.content };
      if (activeChapter.updated_at) {
        body.if_unchanged_since = activeChapter.updated_at;
      }
      const updated = await api<{ updated_at?: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}`,
        {
          method: 'PATCH',
          body: JSON.stringify(body),
        }
      );
      const merged = { content: data.content, word_count: data.wordCount, updated_at: updated?.updated_at };
      setActiveChapter((prev) =>
        prev ? { ...prev, ...merged } : null
      );
      if (book) {
        setBook({
          ...book,
          chapters: book.chapters.map((c) =>
            c.id === activeChapter.id ? { ...c, ...merged } : c
          ),
        });
      }
    },
    [activeChapter, book, projectId, bookId]
  );

  const { scheduleSave, saveNow, status, lastSaved, hasPending, retry, flushPending } = useAutosave<{
    content: Record<string, unknown>;
    wordCount: number;
  }>({
    onSave: saveChapter,
    delayMs: 2000,
    onError: (err) => {
      const isConflict = err instanceof ApiError && err.status === 409;
      toast({
        title: isConflict
          ? 'Save conflict—someone else may have edited. Try restoring from version history.'
          : "Couldn't save—check your connection and try again",
        variant: 'destructive',
      });
    },
    maxRetries: 5,
    draftKey: activeChapter?.id,
    getDraftPayload: (d) => ({ content: d.content, wordCount: d.wordCount }),
  });

  useUnsavedChangesGuard(hasPending);

  const [recoveryDraft, setRecoveryDraft] = useState<{ content: Record<string, unknown>; wordCount: number } | null>(null);
  const [showSyncFailedBanner, setShowSyncFailedBanner] = useState(false);
  const storageAvailable = isStorageAvailable();

  useEffect(() => {
    if (!activeChapter?.id) {
      setRecoveryDraft(null);
      return;
    }
    const draft = loadDraft(activeChapter.id);
    if (!draft) {
      setRecoveryDraft(null);
      return;
    }
    const serverContent = activeChapter.content;
    const draftContent = draft.content;
    const serverJson = JSON.stringify(serverContent ?? {});
    const draftJson = JSON.stringify(draftContent ?? {});
    if (draftJson !== serverJson) {
      setRecoveryDraft({ content: draftContent, wordCount: draft.wordCount });
    } else {
      clearDraft(activeChapter.id);
      setRecoveryDraft(null);
    }
  }, [activeChapter?.id, activeChapter?.content]);

  useEffect(() => {
    if (status === 'error') setShowSyncFailedBanner(true);
  }, [status]);

  const handleRestoreDraft = useCallback(() => {
    if (!recoveryDraft || !activeChapter) return;
    setActiveChapter((prev) =>
      prev ? { ...prev, content: recoveryDraft.content, word_count: recoveryDraft.wordCount } : null
    );
    if (book) {
      setBook({
        ...book,
        chapters: book.chapters.map((c) =>
          c.id === activeChapter.id
            ? { ...c, content: recoveryDraft.content, word_count: recoveryDraft.wordCount }
            : c
        ),
      });
    }
    saveNow({ content: recoveryDraft.content, wordCount: recoveryDraft.wordCount });
    clearDraft(activeChapter.id);
    setRecoveryDraft(null);
    toast({ title: 'Draft restored' });
  }, [recoveryDraft, activeChapter, book, saveNow, toast]);

  const handleDismissRecovery = useCallback(() => {
    if (recoveryDraft && activeChapter) clearDraft(activeChapter.id);
    setRecoveryDraft(null);
  }, [recoveryDraft, activeChapter?.id]);

  const handleDismissSyncFailed = useCallback(() => setShowSyncFailedBanner(false), []);

  const handleChapterChange = useCallback(
    (content: Record<string, unknown>, wordCount: number) => {
      if (!activeChapter) return;
      setLiveWordCount(wordCount);
      if (wordCount > 0) markFirstWriteDone();
      scheduleSave({ content, wordCount });
    },
    [activeChapter, scheduleSave]
  );

  const handleExport = useCallback(
    async (format: string, backupFilename?: boolean) => {
      try {
        const token = localStorage.getItem('access_token');
        const exportFormat = format === 'backup' ? 'txt' : format;
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || ''}/api/v1/export/books/${bookId}/${exportFormat}`,
          { headers: token ? { Authorization: `Bearer ${token}` } : {} }
        );
        if (!res.ok) throw new Error('Export failed');
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const base = book?.title || 'book';
        a.download = backupFilename
          ? `${base}-backup-${new Date().toISOString().slice(0, 10)}.${exportFormat}`
          : `${base}.${exportFormat}`;
        a.click();
        URL.revokeObjectURL(url);
        toast({ title: backupFilename ? 'Backup downloaded' : 'Export started' });
      } catch {
        toast({ title: "Export didn't complete—please try again", variant: 'destructive' });
      }
    },
    [bookId, book?.title, toast]
  );

  const handleSelectChapter = useCallback(
    (ch: { id: string }) => {
      void (async () => {
        await flushPending();
        const full = book?.chapters.find((c) => c.id === ch.id);
        if (full) setActiveChapter(full);
      })();
    },
    [flushPending, book?.chapters]
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

  const handleRenameChapter = useCallback(
    async (chapterId: string, newTitle: string) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}`, {
          method: 'PATCH',
          body: JSON.stringify({ title: newTitle }),
        });
        setBook((b) =>
          b ? { ...b, chapters: b.chapters.map((c) => (c.id === chapterId ? { ...c, title: newTitle } : c)) } : null
        );
        setActiveChapter((prev) => (prev?.id === chapterId ? { ...prev, title: newTitle } : prev));
        toast({ title: 'Chapter renamed' });
      } catch {
        toast({ title: 'Failed to rename', variant: 'destructive' });
      }
    },
    [projectId, bookId, toast]
  );

  const handleDuplicateChapter = useCallback(
    async (chapterId: string) => {
      try {
        const ch = await api<Chapter>(
          `/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}/duplicate`,
          { method: 'POST' }
        );
        setBook((b) => (b ? { ...b, chapters: [...b.chapters, ch] } : null));
        setActiveChapter(ch);
        toast({ title: 'Chapter duplicated' });
      } catch {
        toast({ title: 'Failed to duplicate', variant: 'destructive' });
      }
    },
    [projectId, bookId, toast]
  );

  const handleDeleteChapter = useCallback(
    async (chapterId: string) => {
      if (!book) return;
      if (book.chapters.length <= 1) {
        toast({ title: 'Cannot delete the only chapter', variant: 'destructive' });
        return;
      }
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}`, {
          method: 'DELETE',
        });
        const next = book.chapters.find((c) => c.id !== chapterId);
        setBook((b) => (b ? { ...b, chapters: b.chapters.filter((c) => c.id !== chapterId) } : null));
        setActiveChapter(activeChapter?.id === chapterId ? (next ?? null) : activeChapter);
        toast({ title: 'Chapter deleted' });
      } catch {
        toast({ title: 'Failed to delete', variant: 'destructive' });
      }
    },
    [projectId, bookId, book, activeChapter, toast]
  );

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
        fetchFinishMode();
      } catch {
        toast({ title: 'Failed to update status', variant: 'destructive' });
      }
    },
    [activeChapter, book, projectId, bookId, toast, fetchFinishMode]
  );

  const handleSectionGroupChange = useCallback(
    async (chapterId: string, sectionGroup: string | null) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}`, {
          method: 'PATCH',
          body: JSON.stringify({ section_group: sectionGroup || null }),
        });
        const val = sectionGroup || null;
        setActiveChapter((prev) => (prev?.id === chapterId ? { ...prev, section_group: val } : prev));
        if (book) {
          setBook({
            ...book,
            chapters: book.chapters.map((c) =>
              c.id === chapterId ? { ...c, section_group: val } : c
            ),
          });
        }
      } catch {
        toast({ title: 'Failed to update section', variant: 'destructive' });
      }
    },
    [book, projectId, bookId, toast]
  );

  const handleTagsChange = useCallback(
    async (chapterId: string, tags: string[]) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}`, {
          method: 'PATCH',
          body: JSON.stringify({ tags }),
        });
        setActiveChapter((prev) => (prev?.id === chapterId ? { ...prev, tags } : prev));
        if (book) {
          setBook({
            ...book,
            chapters: book.chapters.map((c) => (c.id === chapterId ? { ...c, tags } : c)),
          });
        }
      } catch {
        toast({ title: 'Failed to update tags', variant: 'destructive' });
      }
    },
    [book, projectId, bookId, toast]
  );

  const handleEnterFinishMode = useCallback(async () => {
    try {
      const updated = await api<FinishModeStats>(
        `/api/v1/projects/${projectId}/books/${bookId}/finish-mode`,
        { method: 'PATCH', body: JSON.stringify({ enabled: true }) }
      );
      setFinishModeStats(updated);
      if (updated.next_chapter_id) {
        const ch = book?.chapters.find((c) => c.id === updated.next_chapter_id);
        if (ch) setActiveChapter(ch);
      }
      toast({ title: 'Finish Mode on', description: 'Focus on crossing the finish line.' });
    } catch {
      toast({ title: 'Failed to enable', variant: 'destructive' });
    }
  }, [projectId, bookId, book?.chapters, toast]);

  const handleExitFinishMode = useCallback(async () => {
    try {
      const updated = await api<FinishModeStats>(
        `/api/v1/projects/${projectId}/books/${bookId}/finish-mode`,
        { method: 'PATCH', body: JSON.stringify({ enabled: false }) }
      );
      setFinishModeStats(updated);
      toast({ title: 'Finish Mode off' });
    } catch {
      toast({ title: 'Failed to disable', variant: 'destructive' });
    }
  }, [projectId, bookId, toast]);

  const handleFinishModeSettingsSave = useCallback(
    async (targetDate: string | null, wordsPerDay: number) => {
      try {
        const updated = await api<FinishModeStats>(
          `/api/v1/projects/${projectId}/books/${bookId}/finish-mode`,
          {
            method: 'PATCH',
            body: JSON.stringify({ target_date: targetDate, words_per_day: wordsPerDay }),
          }
        );
        setFinishModeStats(updated);
        toast({ title: 'Settings saved' });
      } catch {
        toast({ title: 'Failed to save', variant: 'destructive' });
      }
    },
    [projectId, bookId, toast]
  );

  const handleJumpToNextChapter = useCallback(
    (chapterId: string) => {
      const chapters = [...(book?.chapters ?? [])].sort((a, b) => a.sort_order - b.sort_order);
      const ch = chapters.find((c) => c.id === chapterId);
      if (ch) setActiveChapter(ch);
    },
    [book?.chapters]
  );

  const handleRecoveryCenterRestore = useCallback(
    (chapterId: string, content: Record<string, unknown>, wordCount: number) => {
      const ch = book?.chapters.find((c) => c.id === chapterId);
      if (!ch || !book) return;
      const updated = { ...ch, content, word_count: wordCount };
      setActiveChapter(updated);
      setBook({
        ...book,
        chapters: book.chapters.map((c) => (c.id === chapterId ? updated : c)),
      });
      saveNow({ content, wordCount });
      setRecoveryDraft(null);
      toast({ title: 'Draft restored' });
    },
    [book, saveNow, toast]
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
      clearDraft(activeChapter.id);
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

  const handleCheckpoint = useCallback(async () => {
    if (!activeChapter) return;
    // Save current editor content first so snapshot captures latest state
    const content = editorRef.current?.getJSON();
    if (content && typeof content === 'object') {
      const plain = tiptapToPlainText(content as Record<string, unknown>);
      const wordCount = plain.split(/\s+/).filter(Boolean).length;
      await saveChapter({ content: content as Record<string, unknown>, wordCount });
    }
    await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}/snapshot`, {
      method: 'POST',
    });
    await loadVersions();
    toast({ title: 'Checkpoint created' });
  }, [projectId, bookId, activeChapter?.id, saveChapter, loadVersions, toast]);

  useEffect(() => {
    if (showHistory && activeChapter) loadVersions();
  }, [showHistory, activeChapter?.id, loadVersions]);

  useEffect(() => {
    setLiveWordCount(null);
  }, [activeChapter?.id]);

  const totalWords = book?.chapters.reduce((s, c) => s + c.word_count, 0) ?? 0;
  const sortedChapters = [...(book?.chapters ?? [])].sort((a, b) => a.sort_order - b.sort_order);

  const documentText =
    activeChapter?.content && typeof activeChapter.content === 'object'
      ? tiptapToPlainText(activeChapter.content as Record<string, unknown>)
      : '';

  const currentWordCount = liveWordCount ?? activeChapter?.word_count ?? 0;
  const showFirstWritePrompt =
    activeChapter &&
    currentWordCount === 0 &&
    !hasCompletedFirstWrite() &&
    !finishModeStats?.is_complete;
  const showFirstWriteProgress =
    activeChapter &&
    hasCompletedFirstWrite() &&
    currentWordCount > 0 &&
    currentWordCount <= 150 &&
    !finishModeStats?.is_complete;

  const handleGenerateStarter = useCallback(async () => {
    if (!activeChapter || !editorRef.current) return;
    setGeneratingStarter(true);
    let text = '';
    try {
      await apiStream(
        '/api/v1/ai/complete',
        (chunk) => { text += chunk; },
        {
          method: 'POST',
          body: JSON.stringify({
            prompt: 'Generate an opening paragraph for this chapter. Write a compelling, engaging start that draws the reader in. One paragraph only.',
            chapter_id: activeChapter.id,
            book_id: bookId,
          }),
        }
      );
      const trimmed = text.trim();
      if (trimmed) {
        editorRef.current.commands.setContent({
          type: 'doc',
          content: [{ type: 'paragraph', content: [{ type: 'text', text: trimmed }] }],
        });
        const wordCount = trimmed.split(/\s+/).filter(Boolean).length;
        markFirstWriteDone();
        scheduleSave({ content: editorRef.current.getJSON(), wordCount });
      }
    } catch {
      toast({ title: 'AI not available', variant: 'destructive' });
    } finally {
      setGeneratingStarter(false);
    }
  }, [activeChapter, bookId, scheduleSave, toast]);

  const handleFocusEditor = useCallback(() => {
    editorRef.current?.commands.focus();
  }, []);

  const handleOutlineChapter = useCallback(() => {
    setPanelMode('ai');
  }, []);

  const handleAddComment = useCallback(
    async (startOffset: number, endOffset: number, body: string) => {
      if (!activeChapter) return;
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${activeChapter.id}/comments`, {
          method: 'POST',
          body: JSON.stringify({ start_offset: startOffset, end_offset: endOffset, body }),
        });
        toast({ title: 'Comment added' });
      } catch {
        toast({ title: 'Failed to add comment', variant: 'destructive' });
      }
    },
    [projectId, bookId, activeChapter?.id, toast]
  );

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

  const finishModeActive = finishModeStats?.enabled ?? false;
  const sprintStartWordsRef = useRef(0);
  const onSprintStart = useCallback(() => {
    sprintStartWordsRef.current = totalWords;
  }, [totalWords]);
  const getSprintWordsWritten = useCallback(
    () => Math.max(0, totalWords - sprintStartWordsRef.current),
    [totalWords]
  );

  const sidebarProps = {
    collapsed: sidebarCollapsed,
    onToggleCollapse: toggleSidebar,
    position: sidebarPosition,
  };

  return (
    <div className={cn('flex h-[calc(100vh-0px)] min-w-0 overflow-hidden', darkMode && 'dark')}>
      {sidebarPosition === 'left' && !distractionFree && !finishModeActive && (
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
          onImportChapter={() => setShowImport(true)}
          onRenameChapter={handleRenameChapter}
          onDuplicateChapter={handleDuplicateChapter}
          onDeleteChapter={handleDeleteChapter}
          onSectionGroupChange={handleSectionGroupChange}
          onTagsChange={handleTagsChange}
          canEnterFinishMode={finishModeStats?.can_enter_finish_mode}
          suggestFinishMode={finishModeStats?.suggest_finish_mode}
          onEnterFinishMode={handleEnterFinishMode}
          {...sidebarProps}
        />
      )}
      {sidebarPosition === 'left' && !distractionFree && finishModeActive && finishModeStats && (
        <FinishModeSidebar
          bookTitle={book?.title ?? 'Book'}
          projectId={projectId}
          bookId={bookId}
          stats={finishModeStats}
          activeChapterId={activeChapter?.id ?? null}
          onSelectChapter={(id) => handleJumpToNextChapter(id)}
          onExitFinishMode={handleExitFinishMode}
          {...sidebarProps}
        />
      )}

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {!distractionFree && finishModeActive && finishModeStats && (
          <header className="flex flex-wrap items-center gap-4 border-b px-4 py-3">
            <FinishModePanel
              stats={finishModeStats}
              onJumpToNext={handleJumpToNextChapter}
              onExitFinishMode={handleExitFinishMode}
              bookId={bookId}
              getWordsWritten={getSprintWordsWritten}
              compact
            />
            <div className="flex items-center gap-2 ml-auto">
              <Button variant="ghost" size="sm" onClick={() => setShowFinishModeSettings(true)}>
                Settings
              </Button>
              <span className="text-sm text-muted-foreground truncate max-w-[200px]">
                {activeChapter?.title ?? 'Select chapter'}
              </span>
              <span className="text-sm font-medium">{totalWords.toLocaleString()} words</span>
              <Button variant="ghost" size="sm" onClick={() => setDistractionFree(true)}>
                Focus
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport('docx')}>
                Export
              </Button>
            </div>
          </header>
        )}
        {!distractionFree && !finishModeActive && (
          <EditorToolbar
            chapterTitle={activeChapter?.title ?? 'Select a chapter'}
            chapterWordCount={activeChapter?.word_count ?? 0}
            totalWordCount={totalWords}
            bookId={bookId}
            saveStatus={status}
            lastSaved={lastSaved}
            hasPending={hasPending}
            onRetry={retry}
            distractionFree={distractionFree}
            darkMode={darkMode}
            panelMode={panelMode}
            onToggleDistractionFree={() => setDistractionFree(true)}
            onToggleDarkMode={() => setDarkMode((d) => !d)}
            onTogglePanel={setPanelMode}
            onExport={handleExport}
            onHistory={() => setShowHistory(true)}
            onRecoveryCenter={() => setShowRecoveryCenter(true)}
            onFindReplace={() => setShowFindReplace(true)}
            onQuickInsert={() => setShowQuickInsert(true)}
            onStatusChange={handleStatusChange}
            sectionStatus={activeChapter?.section_status}
            showAi={!!book?.type}
            sidebarPosition={sidebarPosition}
            onSidebarPositionChange={setSidebarPosition}
          />
        )}

        {distractionFree && (
          <div className="flex items-center justify-between border-b px-4 py-2">
            <span className="text-sm text-muted-foreground">Focus mode — stay with the page</span>
            <div className="flex items-center gap-3">
              {status === 'saving' && <span className="text-xs text-muted-foreground">Saving…</span>}
              {status === 'saved' && lastSaved && (
                <span className="text-xs text-green-600 dark:text-green-500">
                  {Date.now() - lastSaved.getTime() < 60_000 ? 'Last saved just now' : `Saved ${Math.floor((Date.now() - lastSaved.getTime()) / 60_000)}m ago`}
                </span>
              )}
              {status === 'error' && (
                <span className="text-xs text-destructive">Save failed</span>
              )}
              {status === 'idle' && hasPending && (
                <span className="text-xs text-muted-foreground">Unsaved</span>
              )}
              <button
                type="button"
                className="text-sm text-primary hover:underline"
                onClick={() => setDistractionFree(false)}
              >
                Exit
              </button>
            </div>
          </div>
        )}

        {(recoveryDraft || showSyncFailedBanner || !storageAvailable) && (
          <div className="space-y-2 border-b px-4 py-2">
            {recoveryDraft && (
              <RecoveryBanner
                variant="draft"
                onRestore={handleRestoreDraft}
                onDismiss={handleDismissRecovery}
              />
            )}
            {showSyncFailedBanner && status === 'error' && (
              <RecoveryBanner
                variant="sync-failed"
                onRetry={retry}
                onDismiss={handleDismissSyncFailed}
              />
            )}
            {!storageAvailable && (
              <div
                role="status"
                className="flex items-center gap-2 rounded-lg border border-amber-500/30 bg-amber-500/5 px-4 py-2 text-sm text-amber-800 dark:text-amber-200"
              >
                Local storage is unavailable. Draft recovery after a crash will not be possible. Consider exporting a backup.
              </div>
            )}
          </div>
        )}

        <div className="flex flex-1 min-h-0">
          {finishModeActive && finishModeStats?.is_complete ? (
            <div className="flex-1 overflow-auto flex items-center justify-center">
              <FinishModeCompletionCeremony
                bookTitle={book?.title ?? 'Your book'}
                totalWords={totalWords}
                chaptersTotal={finishModeStats.chapters_total}
                onExport={(format) => handleExport(format === 'backup' ? 'backup' : 'docx', format === 'backup')}
                onExit={handleExitFinishMode}
              />
            </div>
          ) : (
          <div className={cn('flex-1 overflow-auto min-w-0', distractionFree ? 'p-4 sm:p-8 max-w-3xl mx-auto' : 'p-3 sm:p-6')}>
            {activeChapter ? (
              <>
              {showFirstWritePrompt && (
                <div className="mb-4 min-w-0 sm:mb-6">
                  <FirstWritePromptBlock
                    onStartWriting={handleFocusEditor}
                    onGenerateIdea={handleGenerateStarter}
                    onOutlineChapter={handleOutlineChapter}
                    onPromptClick={(p) => {
                      if (p === 'firstSentence') handleFocusEditor();
                      else setPanelMode('ai');
                    }}
                    onAiAssist={(a) => {
                      if (a === 'generateStarter') handleGenerateStarter();
                      else setPanelMode('ai');
                    }}
                  />
                  {generatingStarter && (
                    <p className="mt-2 text-sm text-muted-foreground">Generating…</p>
                  )}
                </div>
              )}
              {showFirstWriteProgress && (
                <div className="mb-4">
                  <FirstWriteProgress wordCount={currentWordCount} />
                </div>
              )}
              <EditorReferenceContextMenu
                selection={editorSelection}
                onLookup={handleLookup}
                onAddComment={handleAddComment}
                editorRef={editorRef}
              >
                <WritingStudioEditor
                content={activeChapter.content}
                onChange={handleChapterChange}
                placeholder="Start where the words are ready."
                distractionFree={distractionFree}
                editorRef={editorRef}
                onSelectionChange={setEditorSelection}
                onLookup={handleLookup}
              />
              </EditorReferenceContextMenu>
              </>
            ) : (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                Pick a chapter from the sidebar, or add one to begin
              </div>
            )}
          </div>
          )}

          {panelMode === 'ai' && book && !finishModeStats?.is_complete && (
            <AIWritingPanel
              projectId={projectId}
              bookId={bookId}
              bookType={book.type === 'fiction' ? 'fiction' : book.type === 'nonfiction' ? 'nonfiction' : undefined}
              chapterId={activeChapter?.id}
              selection={editorSelection}
              isFiction={book.type === 'fiction'}
              isNonfiction={book.type === 'nonfiction'}
              onClose={() => setPanelMode('none')}
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

          {panelMode === 'revision' && book && (
            <RevisionPanel
              projectId={projectId}
              bookId={bookId}
              chapters={sortedChapters}
              activeChapterId={activeChapter?.id ?? null}
              onSelectChapter={(id) => handleSelectChapter({ id } as Chapter)}
            />
          )}

          {panelMode === 'vault' && activeChapter && (
            <VaultKnowledgePanel
              projectId={projectId}
              bookId={bookId}
              chapterId={activeChapter.id}
            />
          )}

          {panelMode === 'integrity' && storyIntegrityEnabled && (
            <StoryIntegrityPanel
              projectId={projectId}
              bookId={bookId}
              activeChapterId={activeChapter?.id ?? null}
              onSelectChapter={(id) => handleSelectChapter({ id } as Chapter)}
              densityEnabled={storyDensityEnabled}
            />
          )}
        </div>
      </div>

      {sidebarPosition === 'right' && !distractionFree && !finishModeActive && (
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
          onImportChapter={() => setShowImport(true)}
          onRenameChapter={handleRenameChapter}
          onDuplicateChapter={handleDuplicateChapter}
          onDeleteChapter={handleDeleteChapter}
          onSectionGroupChange={handleSectionGroupChange}
          onTagsChange={handleTagsChange}
          canEnterFinishMode={finishModeStats?.can_enter_finish_mode}
          suggestFinishMode={finishModeStats?.suggest_finish_mode}
          onEnterFinishMode={handleEnterFinishMode}
          {...sidebarProps}
        />
      )}
      {sidebarPosition === 'right' && !distractionFree && finishModeActive && finishModeStats && (
        <FinishModeSidebar
          bookTitle={book?.title ?? 'Book'}
          projectId={projectId}
          bookId={bookId}
          stats={finishModeStats}
          activeChapterId={activeChapter?.id ?? null}
          onSelectChapter={(id) => handleJumpToNextChapter(id)}
          onExitFinishMode={handleExitFinishMode}
          {...sidebarProps}
        />
      )}

      <FindReplaceDialog
        open={showFindReplace}
        onOpenChange={setShowFindReplace}
        editorRef={editorRef}
        chapters={book?.chapters ?? []}
        activeChapterId={activeChapter?.id ?? null}
        onSelectChapter={(id) => handleSelectChapter({ id } as Chapter)}
      />
      <VersionHistoryDialog
        open={showHistory}
        onOpenChange={setShowHistory}
        versions={versions}
        loading={versionsLoading}
        onRestore={handleRestoreVersion}
        onCheckpoint={handleCheckpoint}
      />
      <RecoveryCenterDialog
        open={showRecoveryCenter}
        onOpenChange={setShowRecoveryCenter}
        chapters={book?.chapters ?? []}
        onRestore={handleRecoveryCenterRestore}
      />
      <QuickInsertDialog
        open={showQuickInsert}
        onOpenChange={setShowQuickInsert}
        editorRef={editorRef}
      />
      <ImportDocumentDialog
        projectId={projectId}
        bookId={bookId}
        onImported={() => {
          // Refresh the book to get new chapters
          api<Book>(`/api/v1/projects/${projectId}/books/${bookId}`)
            .then((b) => {
              setBook(b);
              if (b.chapters.length > 0 && !activeChapter) {
                setActiveChapter(b.chapters[0]);
              }
            })
            .catch(() => {});
        }}
        trigger={<span className="hidden" />}
        open={showImport}
        onOpenChange={setShowImport}
      />
      <FinishModeSettingsDialog
        open={showFinishModeSettings}
        onOpenChange={setShowFinishModeSettings}
        currentTargetDate={finishModeStats?.target_date ?? null}
        currentWordsPerDay={finishModeStats?.words_per_day ?? 500}
        onSave={handleFinishModeSettingsSave}
      />

      {/* Tutorial overlays — shown once, dismissible */}
      {panelMode === 'ai' && shouldShowOverlay('ai_first') && (
        <GuidedOverlay
          tutorialId="ai_first"
          onComplete={() => markCompleted('ai_first')}
          onSkip={() => markDismissed('ai_first')}
        />
      )}
      {panelMode === 'integrity' && shouldShowOverlay('integrity_first') && (
        <GuidedOverlay
          tutorialId="integrity_first"
          onComplete={() => markCompleted('integrity_first')}
          onSkip={() => markDismissed('integrity_first')}
        />
      )}
    </div>
  );
}
