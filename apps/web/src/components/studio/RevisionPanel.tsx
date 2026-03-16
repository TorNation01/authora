'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { FileText, Filter, Plus } from 'lucide-react';
import { ChapterApprovalSection } from './ChapterApprovalSection';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { REVISION_PASS_TYPES } from '@/content/editor-copy';
import { useToast } from '@/hooks/use-toast';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  word_count: number;
  section_status?: string | null;
}

interface ContentComment {
  id: string;
  user_id?: string | null;
  chapter_id: string | null;
  revision_pass_id?: string | null;
  body: string;
  resolved_at: string | null;
  created_at: string;
  replies: ContentComment[];
  user_email?: string | null;
  user_display_name?: string | null;
}

interface RevisionPass {
  id: string;
  pass_type: string;
  name: string | null;
  sort_order: number;
  completed_at: string | null;
  chapters_total: number;
  chapters_completed: number;
  unresolved_comments: number;
}

interface RevisionPassSummary {
  passes: RevisionPass[];
  total_unresolved: number;
}

interface RevisionPanelProps {
  projectId: string;
  bookId: string;
  chapters: Chapter[];
  activeChapterId: string | null;
  onSelectChapter: (chapterId: string) => void;
}

export function RevisionPanel({
  projectId,
  bookId,
  chapters,
  activeChapterId,
  onSelectChapter,
}: RevisionPanelProps) {
  const [commentsByChapter, setCommentsByChapter] = useState<Record<string, ContentComment[]>>({});
  const [unresolvedOnly, setUnresolvedOnly] = useState(true);
  const [loading, setLoading] = useState(false);
  const [passes, setPasses] = useState<RevisionPass[]>([]);
  const [activePassId, setActivePassId] = useState<string | null>(null);
  const [showAddPass, setShowAddPass] = useState(false);
  const [newPassType, setNewPassType] = useState<string>('structural');
  const [filterByUserId, setFilterByUserId] = useState<string | null>(null);
  const [reviewers, setReviewers] = useState<Reviewer[]>([]);
  const { toast } = useToast();

  const fetchReviewers = useCallback(async () => {
    try {
      const members = await api<Reviewer[]>(`/api/v1/projects/${projectId}/members`);
      setReviewers(members);
    } catch {
      setReviewers([]);
    }
  }, [projectId]);

  useEffect(() => {
    fetchReviewers();
  }, [fetchReviewers]);

  const chapterIds = chapters.map((c) => c.id).join(',');
  const chaptersRef = useRef(chapters);
  chaptersRef.current = chapters;

  const fetchPasses = useCallback(async () => {
    try {
      const summary = await api<RevisionPassSummary>(
        `/api/v1/projects/${projectId}/revision-passes?book_id=${bookId}`
      );
      setPasses(summary.passes);
    } catch {
      setPasses([]);
    }
  }, [projectId, bookId]);

  useEffect(() => {
    fetchPasses();
  }, [fetchPasses]);

  useEffect(() => {
    const chs = chaptersRef.current;
    if (chs.length === 0) return;
    let cancelled = false;
    setLoading(true);
    const run = async () => {
      const results: Record<string, ContentComment[]> = {};
      for (const ch of chs) {
        if (cancelled) return;
        try {
          let url = `/api/v1/projects/${projectId}/books/${bookId}/chapters/${ch.id}/comments?unresolved_only=${unresolvedOnly}`;
          if (activePassId) url += `&revision_pass_id=${activePassId}`;
          if (filterByUserId) url += `&user_id=${filterByUserId}`;
          const list = await api<ContentComment[]>(url);
          results[ch.id] = list;
        } catch {
          results[ch.id] = [];
        }
      }
      if (!cancelled) setCommentsByChapter(results);
      setLoading(false);
    };
    run();
    return () => { cancelled = true; };
  }, [chapterIds, unresolvedOnly, projectId, bookId, activePassId, filterByUserId]);

  const handleAddPass = useCallback(async () => {
    try {
      await api(`/api/v1/projects/${projectId}/revision-passes`, {
        method: 'POST',
        body: JSON.stringify({ book_id: bookId, pass_type: newPassType }),
      });
      await fetchPasses();
      setShowAddPass(false);
      toast({ title: 'Revision pass added' });
    } catch {
      toast({ title: 'Failed to add pass', variant: 'destructive' });
    }
  }, [projectId, bookId, newPassType, fetchPasses, toast]);

  const totalUnresolved = Object.values(commentsByChapter).reduce(
    (sum, list) => sum + list.filter((c) => !c.resolved_at).length,
    0
  );

  const sortedChapters = [...chapters].sort((a, b) => a.sort_order - b.sort_order);
  const activePass = passes.find((p) => p.id === activePassId);

  return (
    <div className="flex h-full flex-col">
      <ChapterApprovalSection
        projectId={projectId}
        bookId={bookId}
        chapters={chapters}
        onSelectChapter={onSelectChapter}
      />
      <div className="border-b p-3 space-y-2">
        <h3 className="font-semibold text-sm">Revision Mode</h3>
        <p className="text-xs text-muted-foreground">
          Work through the manuscript one issue at a time
        </p>
        <div className="flex flex-wrap gap-2">
          <Select value={activePassId ?? 'all'} onValueChange={(v) => setActivePassId(v === 'all' ? null : v)}>
            <SelectTrigger className="h-8 text-xs w-[140px]">
              <SelectValue placeholder="Filter by pass" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All passes</SelectItem>
              {passes.map((p) => (
                <SelectItem key={p.id} value={p.id}>
                  {REVISION_PASS_TYPES.find((t) => t.value === p.pass_type)?.label ?? p.name ?? p.pass_type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs"
            onClick={() => setShowAddPass(true)}
          >
            <Plus className="h-3 w-3 mr-1" />
            Add pass
          </Button>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Select
            value={filterByUserId ?? 'all'}
            onValueChange={(v) => setFilterByUserId(v === 'all' ? null : v)}
          >
            <SelectTrigger className="h-8 text-xs w-[140px]">
              <SelectValue placeholder="Filter by reviewer" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All reviewers</SelectItem>
              {reviewers.map((r) => (
                <SelectItem key={r.user_id} value={r.user_id}>
                  {r.display_name || r.email || r.user_id}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant={unresolvedOnly ? 'secondary' : 'ghost'}
            size="sm"
            className="text-xs"
            onClick={() => setUnresolvedOnly(!unresolvedOnly)}
          >
            <Filter className="h-3 w-3 mr-1" />
            Unresolved only
          </Button>
          <span className="text-xs text-muted-foreground">
            {totalUnresolved} unresolved
          </span>
        </div>
        {activePass && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>{activePass.chapters_completed}/{activePass.chapters_total} chapters</span>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-auto p-2">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : (
          <div className="space-y-2">
            {sortedChapters.map((ch) => {
              const comments = commentsByChapter[ch.id] ?? [];
              const unresolved = comments.filter((c) => !c.resolved_at);
              const count = unresolvedOnly ? unresolved.length : comments.length;
              if (count === 0) return null;
              return (
                <button
                  key={ch.id}
                  type="button"
                  onClick={() => onSelectChapter(ch.id)}
                  className={`w-full text-left rounded-lg border p-2 transition-colors ${
                    activeChapterId === ch.id
                      ? 'border-primary bg-primary/5'
                      : 'hover:bg-muted/50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <span className="font-medium text-sm truncate">{ch.title}</span>
                    <span className="text-xs text-muted-foreground ml-auto">
                      {count} {count === 1 ? 'note' : 'notes'}
                    </span>
                  </div>
                  {unresolved.length > 0 && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                      {unresolved.length} unresolved
                    </p>
                  )}
                </button>
              );
            })}
          </div>
        )}
        {!loading && totalUnresolved === 0 && (
          <p className="text-sm text-muted-foreground py-4 text-center">
            No revision notes. Add comments as you read through your draft.
          </p>
        )}
      </div>

      <Dialog open={showAddPass} onOpenChange={setShowAddPass}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add revision pass</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <label className="text-sm font-medium">Pass type</label>
              <Select value={newPassType} onValueChange={setNewPassType}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {REVISION_PASS_TYPES.map((t) => (
                    <SelectItem key={t.value} value={t.value}>
                      {t.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowAddPass(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddPass}>Add pass</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
