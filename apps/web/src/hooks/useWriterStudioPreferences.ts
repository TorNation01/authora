'use client';

import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'authora-writer-studio-preferences';

export type SidebarPosition = 'left' | 'right';

export interface WriterStudioPreferences {
  /** Chapters sidebar position: left (default) or right. Right-handed often prefer left; left-handed may prefer right. */
  sidebarPosition: SidebarPosition;
  /** Chapters sidebar collapsed to give more space to the editor */
  sidebarCollapsed: boolean;
  /** Right panel (AI, notes, etc.) collapsed */
  rightPanelCollapsed: boolean;
}

const DEFAULT: WriterStudioPreferences = {
  sidebarPosition: 'left',
  sidebarCollapsed: false,
  rightPanelCollapsed: true, // starts closed; user opens as needed
};

function load(): WriterStudioPreferences {
  if (typeof window === 'undefined') return DEFAULT;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return DEFAULT;
    const parsed = JSON.parse(raw) as Partial<WriterStudioPreferences>;
    return {
      sidebarPosition: parsed.sidebarPosition === 'right' ? 'right' : 'left',
      sidebarCollapsed: Boolean(parsed.sidebarCollapsed),
      rightPanelCollapsed: parsed.rightPanelCollapsed ?? DEFAULT.rightPanelCollapsed,
    };
  } catch {
    return DEFAULT;
  }
}

function save(prefs: WriterStudioPreferences) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch {
    // ignore
  }
}

export function useWriterStudioPreferences() {
  const [prefs, setPrefs] = useState<WriterStudioPreferences>(DEFAULT);

  useEffect(() => {
    setPrefs(load());
  }, []);

  const update = useCallback((updates: Partial<WriterStudioPreferences>) => {
    setPrefs((prev) => {
      const next = { ...prev, ...updates };
      save(next);
      return next;
    });
  }, []);

  const setSidebarPosition = useCallback(
    (position: SidebarPosition) => update({ sidebarPosition: position }),
    [update]
  );

  const setSidebarCollapsed = useCallback(
    (collapsed: boolean) => update({ sidebarCollapsed: collapsed }),
    [update]
  );

  const setRightPanelCollapsed = useCallback(
    (collapsed: boolean) => update({ rightPanelCollapsed: collapsed }),
    [update]
  );

  const toggleSidebar = useCallback(
    () => setSidebarCollapsed(!prefs.sidebarCollapsed),
    [prefs.sidebarCollapsed, setSidebarCollapsed]
  );

  return {
    ...prefs,
    setSidebarPosition,
    setSidebarCollapsed,
    setRightPanelCollapsed,
    toggleSidebar,
    update,
  };
}
