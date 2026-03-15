'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

type HelpContextValue = {
  isHelpCenterOpen: boolean;
  openHelpCenter: (articleId?: string) => void;
  closeHelpCenter: () => void;
  /** Article to show when opening (e.g. from contextual help) */
  initialArticleId: string | null;
  setInitialArticleId: (id: string | null) => void;
  /** First-use: has user completed onboarding/walkthrough? */
  hasSeenFirstUse: boolean;
  markFirstUseSeen: () => void;
  /** Start a walkthrough by id */
  startWalkthrough: (id: string) => void;
  activeWalkthrough: string | null;
  endWalkthrough: () => void;
};

const HelpContext = createContext<HelpContextValue | null>(null);

const FIRST_USE_KEY = 'authora_help_first_use_seen';

export function HelpProvider({ children }: { children: React.ReactNode }) {
  const [isHelpCenterOpen, setIsHelpCenterOpen] = useState(false);
  const [initialArticleId, setInitialArticleId] = useState<string | null>(null);
  const [activeWalkthrough, setActiveWalkthrough] = useState<string | null>(null);
  const [hasSeenFirstUse, setHasSeenFirstUse] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(FIRST_USE_KEY) === '1';
  });

  const openHelpCenter = useCallback((articleId?: string) => {
    setInitialArticleId(articleId ?? null);
    setIsHelpCenterOpen(true);
  }, []);

  const closeHelpCenter = useCallback(() => {
    setIsHelpCenterOpen(false);
    setInitialArticleId(null);
  }, []);

  const markFirstUseSeen = useCallback(() => {
    setHasSeenFirstUse(true);
    if (typeof window !== 'undefined') {
      localStorage.setItem(FIRST_USE_KEY, '1');
    }
  }, []);

  const startWalkthrough = useCallback((id: string) => {
    setActiveWalkthrough(id);
  }, []);

  const endWalkthrough = useCallback(() => {
    setActiveWalkthrough(null);
  }, []);

  const value: HelpContextValue = {
    isHelpCenterOpen,
    openHelpCenter,
    closeHelpCenter,
    initialArticleId,
    setInitialArticleId,
    hasSeenFirstUse,
    markFirstUseSeen,
    startWalkthrough,
    activeWalkthrough,
    endWalkthrough,
  };

  return <HelpContext.Provider value={value}>{children}</HelpContext.Provider>;
}

export function useHelp() {
  const ctx = useContext(HelpContext);
  if (!ctx) {
    return {
      isHelpCenterOpen: false,
      openHelpCenter: () => {},
      closeHelpCenter: () => {},
      initialArticleId: null,
      setInitialArticleId: () => {},
      hasSeenFirstUse: false,
      markFirstUseSeen: () => {},
      startWalkthrough: () => {},
      activeWalkthrough: null,
      endWalkthrough: () => {},
    };
  }
  return ctx;
}
