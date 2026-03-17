/**
 * Conversion trigger detection.
 * Usage limits, momentum, stuck, near completion.
 */

import { useEffect, useState } from 'react';
import { getBillingStatus, canCreateProject } from '@/lib/billing';
import { useUpgradeTrigger } from '@/contexts/UpgradeTriggerContext';
import { useConfig } from '@/contexts/ConfigProvider';

const MOMENTUM_STREAK_THRESHOLD = 3;
const STUCK_DAYS_THRESHOLD = 7;
const NEAR_COMPLETION_PERCENT = 80;

/** Check if error message indicates usage limit. */
export function isLimitError(message: string): boolean {
  return (
    /project limit reached/i.test(message) ||
    /book limit reached/i.test(message) ||
    /ai.*limit/i.test(message) ||
    /export.*limit/i.test(message)
  );
}

/** Hook: show upgrade when usage limit error occurs (call from catch blocks). */
export function useLimitErrorHandler() {
  const { showUpgrade } = useUpgradeTrigger();

  return (err: unknown) => {
    const msg = err instanceof Error ? err.message : String(err);
    if (isLimitError(msg)) {
      showUpgrade('usage_limit');
    }
  };
}

/** Hook: pre-check before create project; show upgrade if at limit. */
export function useProjectCreateGuard() {
  const config = useConfig();
  const { showUpgrade } = useUpgradeTrigger();

  return async (): Promise<boolean> => {
    if (!config.feature_flags.billing) return true;
    try {
      const status = await getBillingStatus();
      if (!canCreateProject(status)) {
        showUpgrade('usage_limit');
        return false;
      }
      return true;
    } catch {
      return true;
    }
  };
}

/** Hook: detect momentum (streak). Returns whether to show upgrade CTA. Component decides when to call showUpgrade. */
export function useMomentumTrigger(streak: number | null) {
  const config = useConfig();
  const [canUpgrade, setCanUpgrade] = useState(false);

  useEffect(() => {
    if (!config.feature_flags.billing || streak == null || streak < MOMENTUM_STREAK_THRESHOLD) {
      return;
    }
    getBillingStatus().then((status) => {
      if (status.can_upgrade && !status.billing_exempt) setCanUpgrade(true);
    });
  }, [config.feature_flags.billing, streak]);

  return canUpgrade;
}

/** Hook: detect near completion. Returns whether to show upgrade CTA. */
export function useNearCompletionTrigger(
  progressPercent: number | null,
  hasFinishModeFeature: boolean
) {
  const config = useConfig();
  const [canUpgrade, setCanUpgrade] = useState(false);

  useEffect(() => {
    if (
      !config.feature_flags.billing ||
      progressPercent == null ||
      progressPercent < NEAR_COMPLETION_PERCENT ||
      hasFinishModeFeature
    ) {
      return;
    }
    getBillingStatus().then((status) => {
      if (status.can_upgrade && !status.billing_exempt) setCanUpgrade(true);
    });
  }, [config.feature_flags.billing, progressPercent, hasFinishModeFeature]);

  return canUpgrade;
}
