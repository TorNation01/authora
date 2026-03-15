/**
 * Billing abstraction - plan status, usage, feature gating.
 * When feature_billing is false, returns premium-equivalent (no limits).
 * Stripe integration: implement in getBillingStatus when ready.
 */

import { api } from './api';

export interface BillingPlan {
  id: string;
  slug: string;
  name: string;
  limits: Record<string, number | number[] | string[]>;
  features: string[];
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
      slug: 'premium',
      name: 'Premium',
      limits: {
        projects: 999,
        books: 999,
        ai_actions_per_month: 500,
        exports_per_month: 50,
        export_formats: ['docx', 'pdf', 'epub', 'txt'],
      },
      features: ['planning', 'editor', 'notes', 'accountability', 'gamification', 'ai', 'ghostwriter', 'export_pdf', 'export_epub', 'publishing_prep'],
    },
    usage: {
      ai_actions: 0,
      ai_actions_limit: 500,
      exports: 0,
      exports_limit: 50,
      projects: 0,
      projects_limit: 999,
      books: 0,
      books_limit: 999,
    },
    billing_exempt: true,
    can_upgrade: false,
  };
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
