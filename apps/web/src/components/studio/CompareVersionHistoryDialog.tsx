'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { tiptapToPlainText } from '@/lib/tiptap-utils';

interface Version {
  id: string;
  chapter_id: string;
  content: Record<string, unknown>;
  word_count: number;
  created_at: string;
}

interface CompareVersionHistoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  versionA: Version;
  versionB: Version;
}

function toPlainText(content: Record<string, unknown>): string {
  try {
    return tiptapToPlainText(content) || '(empty)';
  } catch {
    return '(empty)';
  }
}

export function CompareVersionHistoryDialog({
  open,
  onOpenChange,
  versionA,
  versionB,
}: CompareVersionHistoryDialogProps) {
  const formatDate = (d: string) => new Date(d).toLocaleString();
  const textA = toPlainText(versionA.content);
  const textB = toPlainText(versionB.content);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Compare versions</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Side-by-side comparison of two versions from history.
        </p>
        <div className="grid grid-cols-2 gap-4 flex-1 min-h-0 overflow-auto">
          <div className="flex flex-col">
            <h4 className="text-sm font-medium mb-2">
              Version A — {versionA.word_count} words · {formatDate(versionA.created_at)}
            </h4>
            <div className="flex-1 rounded-lg border bg-muted/30 p-4 overflow-auto">
              <p className="text-sm font-serif whitespace-pre-wrap">{textA}</p>
            </div>
          </div>
          <div className="flex flex-col">
            <h4 className="text-sm font-medium mb-2">
              Version B — {versionB.word_count} words · {formatDate(versionB.created_at)}
            </h4>
            <div className="flex-1 rounded-lg border bg-muted/30 p-4 overflow-auto">
              <p className="text-sm font-serif whitespace-pre-wrap">{textB}</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
