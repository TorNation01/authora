'use client';

import React, { createContext, useContext, useCallback, useState } from 'react';
import { UpgradeModal } from '@/components/conversion/UpgradeModal';
import type { UpgradeTrigger } from '@/content/conversion-copy';

interface UpgradeTriggerContextValue {
  showUpgrade: (trigger: UpgradeTrigger, options?: { featureLabel?: string }) => void;
  hideUpgrade: () => void;
}

const UpgradeTriggerContext = createContext<UpgradeTriggerContextValue | null>(null);

export function UpgradeTriggerProvider({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  const [trigger, setTrigger] = useState<UpgradeTrigger>('feature_locked');
  const [featureLabel, setFeatureLabel] = useState<string | undefined>();

  const showUpgrade = useCallback((t: UpgradeTrigger, opts?: { featureLabel?: string }) => {
    setTrigger(t);
    setFeatureLabel(opts?.featureLabel);
    setOpen(true);
  }, []);

  const hideUpgrade = useCallback(() => setOpen(false), []);

  const value: UpgradeTriggerContextValue = { showUpgrade, hideUpgrade };

  return (
    <UpgradeTriggerContext.Provider value={value}>
      {children}
      <UpgradeModal
        open={open}
        onOpenChange={setOpen}
        trigger={trigger}
        featureLabel={featureLabel}
      />
    </UpgradeTriggerContext.Provider>
  );
}

export function useUpgradeTrigger(): UpgradeTriggerContextValue {
  const ctx = useContext(UpgradeTriggerContext);
  if (!ctx) {
    return {
      showUpgrade: () => {},
      hideUpgrade: () => {},
    };
  }
  return ctx;
}
