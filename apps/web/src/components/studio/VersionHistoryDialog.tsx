'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

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
  const [confirmingVersion, setConfirmingVersion] = useState<Version | null>(null);

  const formatDate = (d: string) => {
    const date = new Date(d);
    return date.toLocaleString();
  };

  const handleRestoreClick = (v: Version) => {
    setConfirmingVersion(v);
  };

  const handleConfirmRestore = () => {
    if (confirmingVersion) {
      onRestore(confirmingVersion);
      setConfirmingVersion(null);
      onOpenChange(false);
    }
  };

  const handleCancelRestore = () => {
    setConfirmingVersion(null);
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Version history</DialogTitle>
            <DialogDescription>
              Restore a previous version. Your current draft will be replaced.
            </DialogDescription>
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
                  <Button variant="outline" size="sm" onClick={() => handleRestoreClick(v)}>
                    Restore
                  </Button>
                </div>
              ))}
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!confirmingVersion} onOpenChange={(o) => !o && handleCancelRestore()}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Restore this version?</DialogTitle>
            <DialogDescription>
              Your current draft will be replaced. This cannot be undone, but you can restore
              another version from history if needed.
            </DialogDescription>
          </DialogHeader>
          {confirmingVersion && (
            <p className="text-sm text-muted-foreground">
              {confirmingVersion.word_count} words · {formatDate(confirmingVersion.created_at)}
            </p>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={handleCancelRestore}>
              Cancel
            </Button>
            <Button onClick={handleConfirmRestore}>Restore</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
