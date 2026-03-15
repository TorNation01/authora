'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Version {
  id: string;
  chapter_id: string;
  content: Record<string, unknown>;
  word_count: number;
  created_at: string;
}

interface VersionHistoryDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  versions: Version[];
  loading?: boolean;
  onRestore: (version: Version) => void;
}

export function VersionHistoryDialog({
  open,
  onOpenChange,
  versions,
  loading,
  onRestore,
}: VersionHistoryDialogProps) {
  const formatDate = (d: string) => {
    const date = new Date(d);
    return date.toLocaleString();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Version history</DialogTitle>
        </DialogHeader>
        <div className="max-h-[60vh] overflow-auto space-y-2">
          {loading && <p className="text-sm text-muted-foreground">Loading...</p>}
          {!loading && versions.length === 0 && (
            <p className="text-sm text-muted-foreground">No versions yet.</p>
          )}
          {!loading &&
            versions.map((v) => (
              <div
                key={v.id}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div>
                  <p className="text-sm font-medium">{v.word_count} words</p>
                  <p className="text-xs text-muted-foreground">{formatDate(v.created_at)}</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => onRestore(v)}>
                  Restore
                </Button>
              </div>
            ))}
        </div>
      </DialogContent>
    </Dialog>
  );
}
