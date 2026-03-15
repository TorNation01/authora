'use client';

import { AlertTriangle, RefreshCw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export type RecoveryBannerVariant = 'draft' | 'sync-failed';

interface RecoveryBannerProps {
  variant: RecoveryBannerVariant;
  onRestore?: () => void;
  onRetry?: () => void;
  onDismiss: () => void;
  className?: string;
}

export function RecoveryBanner({
  variant,
  onRestore,
  onRetry,
  onDismiss,
  className,
}: RecoveryBannerProps) {
  if (variant === 'draft') {
    return (
      <div
        role="alert"
        className={cn(
          'flex items-center justify-between gap-4 rounded-lg border border-amber-500/50 bg-amber-500/10 px-4 py-3 text-sm',
          className
        )}
      >
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-500" />
          <span>
            Unsaved draft found from a previous session. Restore it or continue with the current version.
          </span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {onRestore && (
            <Button size="sm" variant="default" onClick={onRestore}>
              Restore draft
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={onDismiss}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    );
  }

  if (variant === 'sync-failed') {
    return (
      <div
        role="alert"
        className={cn(
          'flex items-center justify-between gap-4 rounded-lg border border-destructive/50 bg-destructive/10 px-4 py-3 text-sm',
          className
        )}
      >
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <span>Changes could not be saved. Your work is stored locally. Try again when you&apos;re back online.</span>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {onRetry && (
            <Button size="sm" variant="outline" onClick={onRetry}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          )}
          <Button size="sm" variant="ghost" onClick={onDismiss}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </div>
    );
  }

  return null;
}
