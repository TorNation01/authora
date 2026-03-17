'use client';

import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

const TUTORIAL_STORAGE_KEY = 'authora_tutorial_progress';

export type TutorialId =
  | 'editor_first'
  | 'ai_first'
  | 'integrity_first'
  | 'density_first'
  | 'integrity_intro'
  | 'density_intro'
  | 'finish_mode_intro';

interface TutorialState {
  completed: TutorialId[];
  dismissed: TutorialId[];
}

function loadState(): TutorialState {
  if (typeof window === 'undefined') return { completed: [], dismissed: [] };
  try {
    const raw = localStorage.getItem(TUTORIAL_STORAGE_KEY);
    if (!raw) return { completed: [], dismissed: [] };
    const parsed = JSON.parse(raw) as TutorialState;
    return {
      completed: Array.isArray(parsed.completed) ? parsed.completed : [],
      dismissed: Array.isArray(parsed.dismissed) ? parsed.dismissed : [],
    };
  } catch {
    return { completed: [], dismissed: [] };
  }
}

function saveState(state: TutorialState) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(TUTORIAL_STORAGE_KEY, JSON.stringify(state));
  } catch {
    /* ignore */
  }
}

type TutorialContextValue = {
  hasCompleted: (id: TutorialId) => boolean;
  hasDismissed: (id: TutorialId) => boolean;
  markCompleted: (id: TutorialId) => void;
  markDismissed: (id: TutorialId) => void;
  shouldShowOverlay: (id: TutorialId) => boolean;
  shouldShowIntroCard: (id: TutorialId) => boolean;
};

const TutorialContext = createContext<TutorialContextValue | null>(null);

export function TutorialProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<TutorialState>(loadState);

  useEffect(() => {
    setState(loadState());
  }, []);

  const save = useCallback((newState: TutorialState) => {
    setState(newState);
    saveState(newState);
  }, []);

  const hasCompleted = useCallback(
    (id: TutorialId) => state.completed.includes(id),
    [state.completed]
  );

  const hasDismissed = useCallback(
    (id: TutorialId) => state.dismissed.includes(id),
    [state.dismissed]
  );

  const markCompleted = useCallback(
    (id: TutorialId) => {
      if (state.completed.includes(id)) return;
      save({
        ...state,
        completed: [...state.completed, id],
      });
    },
    [state, save]
  );

  const markDismissed = useCallback(
    (id: TutorialId) => {
      if (state.dismissed.includes(id)) return;
      save({
        ...state,
        dismissed: [...state.dismissed, id],
      });
    },
    [state, save]
  );

  const shouldShowOverlay = useCallback(
    (id: TutorialId) => !state.completed.includes(id) && !state.dismissed.includes(id),
    [state]
  );

  const shouldShowIntroCard = useCallback(
    (id: TutorialId) => !state.dismissed.includes(id),
    [state.dismissed]
  );

  const value: TutorialContextValue = {
    hasCompleted,
    hasDismissed,
    markCompleted,
    markDismissed,
    shouldShowOverlay,
    shouldShowIntroCard,
  };

  return (
    <TutorialContext.Provider value={value}>{children}</TutorialContext.Provider>
  );
}

export function useTutorial() {
  const ctx = useContext(TutorialContext);
  if (!ctx) {
    return {
      hasCompleted: () => false,
      hasDismissed: () => false,
      markCompleted: () => {},
      markDismissed: () => {},
      shouldShowOverlay: () => false,
      shouldShowIntroCard: () => false,
    };
  }
  return ctx;
}
