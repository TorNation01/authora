'use client';

import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Shield, FileText, RotateCcw, Trash2 } from 'lucide-react';
import { listAllDrafts, loadDraft, clearDraft, type DraftMeta } from '@/lib/draft-storage';

interface Chapter {
  id: string;
  title: string;
}

interface RecoveryCenterDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  chapters: Chapter[];
  onRestore: (chapterId: string, content: Record<string, unknown>, wordCount: number) => void;
}

function formatRelativeTime(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  if (diffMs < 60_000) return 'just now';
  if (diffMs < 3600_000) return `${Math.floor(diffMs / 60_000)}m ago`;
  if (diffMs < 86400_000) return `${Math.floor(diffMs / 3600_000)}h ago`;
  if (diffMs < 7 * 86400_000) return `${Math.floor(diffMs / 86400_000)}d ago`;
  return d.toLocaleDateString();
}

export function RecoveryCenterDialog({
  open,
  onOpenChange,
  chapters,
  onRestore,
}: RecoveryCenterDialogProps) {
  const [drafts, setDrafts] = useState<DraftMeta[]>([]);

  useEffect(() => {
    if (open) setDrafts(listAllDrafts());
  }, [open]);

  const getChapterTitle = (chapterId: string) =>
    chapters.find((c) => c.id === chapterId)?.title ?? `Chapter ${chapterId.slice(0, 8)}…`;

  const handleRestore = (meta: DraftMeta) => {
    const snapshot = loadDraft(meta.chapterId);
    if (!snapshot?.content) return;
    onRestore(meta.chapterId, snapshot.content, meta.wordCount);
    clearDraft(meta.chapterId);
    setDrafts((prev) => prev.filter((d) => d.chapterId !== meta.chapterId));
    onOpenChange(false);
  };

  const handleDismiss = (chapterId: string) => {
    clearDraft(chapterId);
    setDrafts((prev) => prev.filter((d) => d.chapterId !== chapterId));
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-green-600 dark:text-green-500" />
            Recovery Center
          </DialogTitle>
          <DialogDescription>
            Local drafts from previous sessions. Your work is backed up automatically—restore any
            draft to continue where you left off.
          </DialogDescription>
        </DialogHeader>

        {drafts.length === 0 ? (
          <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
            <FileText className="mx-auto mb-2 h-8 w-8 opacity-50" />
            <p>No recoverable drafts.</p>
            <p className="mt-1 text-xs">
              Drafts are saved locally as you write and kept for 7 days.
            </p>
          </div>
        ) : (
          <div className="max-h-[50vh] space-y-2 overflow-auto">
            {drafts.map((d) => (
              <div
                key={d.chapterId}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div>
                  <p className="font-medium">{getChapterTitle(d.chapterId)}</p>
                  <p className="text-xs text-muted-foreground">
                    {d.wordCount} words · {formatRelativeTime(d.savedAt)}
                  </p>
                </div>
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRestore(d)}
                    className="gap-1"
                  >
                    <RotateCcw className="h-3.5 w-3.5" />
                    Restore
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDismiss(d.chapterId)}
                    title="Discard draft"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}

        <p className="text-xs text-muted-foreground">
          Your work is saved automatically. Drafts are stored locally for crash and tab-close
          recovery.
        </p>
      </DialogContent>
    </Dialog>
  );
}
