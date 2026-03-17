'use client';

import React from 'react';
import { Lock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useUpgradeTrigger } from '@/contexts/UpgradeTriggerContext';
import { FEATURE_LABELS } from '@/content/conversion-copy';
import { getBillingStatus, canUseFeature } from '@/lib/billing';
import { useConfig } from '@/contexts/ConfigProvider';

interface FeatureGateProps {
  feature: string;
  children: React.ReactNode;
  className?: string;
  /** If true, render children but make them clickable to show upgrade (locked features visible) */
  showLocked?: boolean;
}

/**
 * Wraps content so it is only accessible when the user has the feature.
 * When locked: if showLocked, children are visible and clickable; click shows upgrade modal.
 * When locked and !showLocked: children are hidden or disabled.
 */
export function FeatureGate({
  feature,
  children,
  className,
  showLocked = true,
}: FeatureGateProps) {
  const { showUpgrade } = useUpgradeTrigger();
  const config = useConfig();
  const [hasAccess, setHasAccess] = React.useState<boolean | null>(null);

  React.useEffect(() => {
    if (!config.feature_flags.billing) {
      setHasAccess(true);
      return;
    }
    getBillingStatus()
      .then((status) => setHasAccess(canUseFeature(status, feature)))
      .catch(() => setHasAccess(true));
  }, [config.feature_flags.billing, feature]);

  const label = FEATURE_LABELS[feature] ?? feature;

  const handleClick = (e: React.MouseEvent) => {
    if (hasAccess) return;
    e.preventDefault();
    e.stopPropagation();
    showUpgrade('feature_locked', { featureLabel: label });
  };

  if (hasAccess === null) {
    return <span className={cn('animate-pulse', className)}>{children}</span>;
  }

  if (hasAccess) {
    return <>{children}</>;
  }

  if (!showLocked) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-md transition-colors hover:bg-muted/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring text-primary hover:underline',
        className
      )}
      aria-label={`${label} — upgrade to unlock`}
    >
      <Lock className="h-4 w-4 shrink-0 text-muted-foreground" />
      {label}
    </button>
  );
}
