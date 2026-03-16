'use client';

import { useCallback, useEffect, useState } from 'react';
import { CheckCircle2, XCircle, AlertCircle, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { APPROVAL_STATUS_LABELS, CHAPTER_APPROVAL_COPY } from '@/content/collaboration-copy';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
}

interface ChapterApproval {
  id: string;
  chapter_id: string;
  status: string;
  approved_by: string | null;
  approved_at: string | null;
  notes: string | null;
}

const STATUS_ICONS: Record<string, React.ReactNode> = {
  pending: <Clock className="h-4 w-4 text-amber-500" />,
  approved: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  rejected: <XCircle className="h-4 w-4 text-red-500" />,
  changes_requested: <AlertCircle className="h-4 w-4 text-amber-500" />,
};

interface ChapterApprovalSectionProps {
  projectId: string;
  bookId: string;
  chapters: Chapter[];
  onSelectChapter?: (chapterId: string) => void;
}

export function ChapterApprovalSection({
  projectId,
  bookId,
  chapters,
  onSelectChapter,
}: ChapterApprovalSectionProps) {
  const [approvals, setApprovals] = useState<ChapterApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);
  const [updating, setUpdating] = useState<string | null>(null);
  const { toast } = useToast();

  const fetchApprovals = useCallback(async () => {
    try {
      const list = await api<ChapterApproval[]>(
        `/api/v1/projects/${projectId}/books/${bookId}/approvals`
      );
      setApprovals(list);
      setHasAccess(true);
    } catch {
      setApprovals([]);
      setHasAccess(false);
    } finally {
      setLoading(false);
    }
  }, [projectId, bookId]);

  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals]);

  async function handleUpdateStatus(chapterId: string, status: string) {
    setUpdating(chapterId);
    try {
      const approval = approvals.find((a) => a.chapter_id === chapterId);
      if (!approval) {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}/approval`, {
          method: 'POST',
        });
      }
      await api(`/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}/approval`, {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      });
      toast({ title: status === 'approved' ? CHAPTER_APPROVAL_COPY.chapterApproved : CHAPTER_APPROVAL_COPY.statusUpdated });
      fetchApprovals();
    } catch {
      toast({ title: 'Failed to update', variant: 'destructive' });
    } finally {
      setUpdating(null);
    }
  }

  if (loading || !hasAccess) return null;
  const sortedChapters = [...chapters].sort((a, b) => a.sort_order - b.sort_order);
  const approvalByChapter = Object.fromEntries(approvals.map((a) => [a.chapter_id, a]));

  return (
    <div className="border-b p-3 space-y-2">
      <h3 className="font-semibold text-sm">{CHAPTER_APPROVAL_COPY.title}</h3>
      <p className="text-xs text-muted-foreground">
        {CHAPTER_APPROVAL_COPY.description}
      </p>
      <div className="space-y-1.5 max-h-48 overflow-auto">
        {sortedChapters.map((ch) => {
          const approval = approvalByChapter[ch.id];
          const status = approval?.status ?? 'pending';
          return (
            <div
              key={ch.id}
              className="flex items-center justify-between gap-2 rounded-lg border p-2 text-sm"
            >
              <button
                type="button"
                onClick={() => onSelectChapter?.(ch.id)}
                className="flex-1 min-w-0 text-left truncate hover:text-primary"
              >
                {ch.title}
              </button>
              <div className="flex items-center gap-2 flex-shrink-0">
                {STATUS_ICONS[status] || STATUS_ICONS.pending}
                <Select
                  value={status}
                  onValueChange={(v) => handleUpdateStatus(ch.id, v)}
                  disabled={updating === ch.id}
                >
                  <SelectTrigger className="h-7 text-xs w-[120px]">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">{APPROVAL_STATUS_LABELS.pending}</SelectItem>
                    <SelectItem value="approved">{APPROVAL_STATUS_LABELS.approved}</SelectItem>
                    <SelectItem value="changes_requested">{APPROVAL_STATUS_LABELS.changes_requested}</SelectItem>
                    <SelectItem value="rejected">{APPROVAL_STATUS_LABELS.rejected}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
