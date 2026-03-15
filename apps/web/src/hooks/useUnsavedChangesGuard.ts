'use client';

import { useEffect } from 'react';

/**
 * Warns user before leaving page when there are unsaved changes.
 * Uses beforeunload for tab close / refresh; does not block in-app navigation.
 */
export function useUnsavedChangesGuard(hasUnsavedChanges: boolean) {
  useEffect(() => {
    if (!hasUnsavedChanges) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [hasUnsavedChanges]);
}
