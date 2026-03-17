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
import { CompareVersionHistoryDialog } from './CompareVersionHistoryDialog';
import { GitCompare } from 'lucide-react';

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
  onCheckpoint?: () => Promise<void>;
}

export function VersionHistoryDialog({
  open,
  onOpenChange,
  versions,
  loading,
  onRestore,
  onCheckpoint,
}: VersionHistoryDialogProps) {
  const [confirmingVersion, setConfirmingVersion] = useState<Version | null>(null);
  const [compareSelection, setCompareSelection] = useState<Version[]>([]);
  const [showCompare, setShowCompare] = useState(false);
  const [checkpointing, setCheckpointing] = useState(false);

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

  const toggleCompareSelection = (v: Version) => {
    setCompareSelection((prev) => {
      const idx = prev.findIndex((x) => x.id === v.id);
      if (idx >= 0) return prev.filter((x) => x.id !== v.id);
      if (prev.length >= 2) return [prev[1], v];
      return [...prev, v];
    });
  };

  const handleCompare = () => {
    if (compareSelection.length === 2) {
      setShowCompare(true);
    }
  };

  const canCompare = compareSelection.length === 2;

  const handleCheckpoint = async () => {
    if (!onCheckpoint) return;
    setCheckpointing(true);
    try {
      await onCheckpoint();
    } finally {
      setCheckpointing(false);
    }
  };

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Version history</DialogTitle>
            <DialogDescription>
              Restore a previous version or compare two versions. Your current draft will be replaced on restore.
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-[60vh] overflow-auto space-y-2">
            {loading && <p className="text-sm text-muted-foreground">Loading...</p>}
            {!loading && versions.length === 0 && (
              <p className="text-sm text-muted-foreground">No versions yet.</p>
            )}
            {!loading &&
              versions.map((v) => {
                const selected = compareSelection.some((x) => x.id === v.id);
                return (
                  <div
                    key={v.id}
                    className="flex items-center justify-between rounded-lg border p-3"
                  >
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        onClick={() => toggleCompareSelection(v)}
                        className={`
                          flex h-5 w-5 shrink-0 items-center justify-center rounded border
                          ${selected ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground/40'}
                        `}
                        aria-label={selected ? 'Deselect for compare' : 'Select for compare'}
                      >
                        {selected && <span className="text-xs font-medium">{compareSelection.findIndex((x) => x.id === v.id) + 1}</span>}
                      </button>
                      <div>
                        <p className="text-sm font-medium">{v.word_count} words</p>
                        <p className="text-xs text-muted-foreground">{formatDate(v.created_at)}</p>
                      </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={() => handleRestoreClick(v)}>
                      Restore
                    </Button>
                  </div>
                );
              })}
          </div>
          <div className="flex justify-end gap-2 pt-2 border-t">
            {onCheckpoint && (
              <Button
                variant="outline"
                size="sm"
                disabled={loading || checkpointing}
                onClick={handleCheckpoint}
              >
                {checkpointing ? 'Creating…' : 'Create checkpoint'}
              </Button>
            )}
            {!loading && versions.length >= 2 && (
              <Button
                variant="outline"
                size="sm"
                disabled={!canCompare}
                onClick={handleCompare}
              >
                <GitCompare className="h-4 w-4 mr-1" />
                Compare selected
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {canCompare && compareSelection[0] && compareSelection[1] && (
        <CompareVersionHistoryDialog
          open={showCompare}
          onOpenChange={setShowCompare}
          versionA={compareSelection[0]}
          versionB={compareSelection[1]}
        />
      )}

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
