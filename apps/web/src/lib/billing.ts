/**
 * Modular billing abstraction.
 * Standalone: no-op (no billing).
 * Anakatech: integrate with shared billing/entitlements.
 */

export interface BillingPlan {
  id: string;
  name: string;
  limits: Record<string, number>;
}

export interface BillingStatus {
  enabled: boolean;
  plan: BillingPlan | null;
  usage: Record<string, number>;
}

export async function getBillingStatus(): Promise<BillingStatus> {
  if (typeof window === 'undefined') return { enabled: false, plan: null, usage: {} };
  const { getConfigSync } = await import('@/lib/config');
  const config = getConfigSync();
  if (!config.feature_flags.billing) {
    return { enabled: false, plan: null, usage: {} };
  }
  // TODO: Call Anakatech billing API
  return { enabled: true, plan: null, usage: {} };
}
