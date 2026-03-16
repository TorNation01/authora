/**
 * Billing abstraction - plan status, usage, feature gating.
 * When feature_billing is false, returns premium-equivalent (no limits).
 * Stripe integration: checkout/create, customer-portal.
 */

import { api } from './api';

export interface PlanPrice {
  monthly_cents: number | null;
  yearly_cents: number | null;
  lifetime_cents: number | null;
}

export interface BillingPlan {
  id: string;
  slug: string;
  name: string;
  limits: Record<string, number | number[] | string[]>;
  features: string[];
  price?: PlanPrice | null;
}

export interface BillingUsage {
  ai_actions: number;
  ai_actions_limit: number;
  exports: number;
  exports_limit: number;
  projects: number;
  projects_limit: number;
  books: number;
  books_limit: number;
  storage_mb?: number;
  storage_mb_limit?: number;
  ghostwriter_sessions?: number;
  ghostwriter_sessions_limit?: number;
}

export interface BillingStatus {
  plan: BillingPlan;
  usage: BillingUsage;
  billing_exempt: boolean;
  can_upgrade: boolean;
  feature_billing_enabled?: boolean;
}

let cachedStatus: BillingStatus | null = null;

export async function getBillingStatus(): Promise<BillingStatus> {
  if (cachedStatus) return cachedStatus;
  try {
    const data = await api<BillingStatus>('/api/v1/billing/status');
    cachedStatus = data;
    return data;
  } catch {
    return getDefaultBillingStatus();
  }
}

export function clearBillingCache(): void {
  cachedStatus = null;
}

function getDefaultBillingStatus(): BillingStatus {
  return {
    plan: {
      id: 'default',
      slug: 'studio',
      name: 'Studio',
      limits: {
        projects: 999,
        books: 999,
        ai_actions_per_month: 1000,
        exports_per_month: 100,
        export_formats: ['docx', 'pdf', 'epub', 'txt'],
      },
      features: ['planning', 'editor', 'notes', 'accountability', 'gamification', 'ai', 'ghostwriter', 'export_pdf', 'export_epub', 'publishing_prep', 'finish_mode', 'semantic_search', 'premium_model_routing'],
    },
    usage: {
      ai_actions: 0,
      ai_actions_limit: 1000,
      exports: 0,
      exports_limit: 100,
      projects: 0,
      projects_limit: 999,
      books: 0,
      books_limit: 999,
    },
    billing_exempt: true,
    can_upgrade: false,
  };
}

export async function createCheckoutSession(planSlug: string, billingInterval: string, promoCode?: string): Promise<{ url: string; session_id: string } | null> {
  try {
    const data = await api<{ url: string; session_id: string }>('/api/v1/billing/checkout/create', {
      method: 'POST',
      body: JSON.stringify({ plan_slug: planSlug, billing_interval: billingInterval, promo_code: promoCode || null }),
    });
    return data;
  } catch {
    return null;
  }
}

export async function createCustomerPortalSession(returnUrl?: string): Promise<{ url: string } | null> {
  try {
    const data = await api<{ url: string }>('/api/v1/billing/customer-portal', {
      method: 'POST',
      body: JSON.stringify({ return_url: returnUrl || null }),
    });
    return data;
  } catch {
    return null;
  }
}

export async function redeemPromoCode(code: string): Promise<{ ok: boolean; plan_slug?: string } | null> {
  try {
    const data = await api<{ ok: boolean; plan_slug?: string }>('/api/v1/billing/redeem-code', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
    return data;
  } catch {
    return null;
  }
}

export function canUseFeature(status: BillingStatus, feature: string): boolean {
  return status.plan.features.includes(feature);
}

export function canCreateProject(status: BillingStatus): boolean {
  const limit = status.plan.limits.projects;
  if (typeof limit === 'number' && limit < 0) return true;
  return status.usage.projects < (typeof limit === 'number' ? limit : 999);
}

export function canCreateBook(status: BillingStatus): boolean {
  const limit = status.plan.limits.books;
  if (typeof limit === 'number' && limit < 0) return true;
  return status.usage.books < (typeof limit === 'number' ? limit : 999);
}

export function canUseAI(status: BillingStatus): boolean {
  return canUseFeature(status, 'ai');
}

export function canExportFormat(status: BillingStatus, format: string): boolean {
  const formats = status.plan.limits.export_formats;
  if (Array.isArray(formats)) {
    return formats.some((f) => String(f).toLowerCase() === format.toLowerCase());
  }
  return true;
}
