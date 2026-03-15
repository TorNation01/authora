'use client';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CompareVersionsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  original: string;
  suggested: string;
  onAccept: () => void;
  onReject: () => void;
}

export function CompareVersionsDialog({
  open,
  onOpenChange,
  original,
  suggested,
  onAccept,
  onReject,
}: CompareVersionsDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle>Compare versions</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Original vs AI suggestion. Accept to replace, reject to keep original.
        </p>
        <div className="grid grid-cols-2 gap-4 flex-1 min-h-0 overflow-auto">
          <div className="flex flex-col">
            <h4 className="text-sm font-medium mb-2">Original</h4>
            <div className="flex-1 rounded-lg border bg-muted/30 p-4 overflow-auto">
              <p className="text-sm font-serif whitespace-pre-wrap">{original || '(empty)'}</p>
            </div>
          </div>
          <div className="flex flex-col">
            <h4 className="text-sm font-medium mb-2">AI suggestion</h4>
            <div className="flex-1 rounded-lg border border-primary/30 bg-primary/5 p-4 overflow-auto">
              <p className="text-sm font-serif whitespace-pre-wrap">{suggested || '(empty)'}</p>
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button variant="outline" onClick={() => { onReject(); onOpenChange(false); }}>
            <X className="h-4 w-4 mr-1" />
            Reject
          </Button>
          <Button onClick={() => { onAccept(); onOpenChange(false); }}>
            <Check className="h-4 w-4 mr-1" />
            Accept
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
