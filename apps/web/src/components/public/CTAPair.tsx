'use client';

import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { CTAButton } from './CTAButton';
import { CTA_ROUTES } from '@/content/cta-copy';

export type PrimaryCTAType = 'start-writing-free' | 'start-free' | 'create-first-book';
export type SecondaryCTAType =
  | 'see-how-it-works'
  | 'view-pricing'
  | 'view-full-pricing'
  | 'explore-features'
  | 'compare-plans'
  | 'create-first-book';

const PRIMARY_CONFIG: Record<
  PrimaryCTAType,
  { label: string; href: (base: string) => string; analytics: string }
> = {
  'start-writing-free': {
    label: 'Start Writing Free',
    href: CTA_ROUTES.register,
    analytics: 'cta-start-writing-free',
  },
  'start-free': {
    label: 'Start Free',
    href: CTA_ROUTES.register,
    analytics: 'cta-start-free',
  },
  'create-first-book': {
    label: 'Create Your First Book',
    href: CTA_ROUTES.register,
    analytics: 'cta-create-first-book',
  },
};

const SECONDARY_CONFIG: Record<
  SecondaryCTAType,
  { label: string; href: string | ((base: string) => string); analytics: string }
> = {
  'see-how-it-works': {
    label: 'See How It Works',
    href: CTA_ROUTES.howItWorks,
    analytics: 'cta-see-how-it-works',
  },
  'view-pricing': {
    label: 'View Pricing',
    href: CTA_ROUTES.pricing,
    analytics: 'cta-view-pricing',
  },
  'view-full-pricing': {
    label: 'View Full Pricing',
    href: CTA_ROUTES.pricing,
    analytics: 'cta-view-full-pricing',
  },
  'explore-features': {
    label: 'Explore Features',
    href: CTA_ROUTES.features,
    analytics: 'cta-explore-features',
  },
  'compare-plans': {
    label: 'Compare Plans',
    href: CTA_ROUTES.pricingCompare,
    analytics: 'cta-compare-plans',
  },
  'create-first-book': {
    label: 'Create Your First Book',
    href: CTA_ROUTES.register,
    analytics: 'cta-create-first-book',
  },
};

interface CTAPairProps {
  primary: PrimaryCTAType;
  secondary?: SecondaryCTAType;
  microcopy?: string;
  analyticsPrefix?: string;
  className?: string;
}

export function CTAPair({
  primary,
  secondary,
  microcopy,
  analyticsPrefix = '',
  className,
}: CTAPairProps) {
  const config = useConfig();
  const { feature_flags } = config;
  const baseUrl = getAppBaseUrl() || '';

  if (!feature_flags.standalone_auth && !feature_flags.sso_ready) {
    return null;
  }

  if (feature_flags.sso_ready && !feature_flags.standalone_auth) {
    return (
      <div className={`flex flex-col items-center gap-4 ${className ?? ''}`}>
        <CTAButton
          href={baseUrl ? `${baseUrl}/sso` : '/sso'}
          label="Sign in"
          variant="primary"
          showArrow={false}
          analyticsId={`${analyticsPrefix}cta-sign-in`}
        />
        {microcopy && (
          <p className="text-sm text-muted-foreground font-medium text-center">{microcopy}</p>
        )}
      </div>
    );
  }

  const p = PRIMARY_CONFIG[primary];
  const s = secondary ? SECONDARY_CONFIG[secondary] : null;

  return (
    <div className={`flex flex-col items-center gap-4 ${className ?? ''}`}>
      <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
        <CTAButton
          href={p.href(baseUrl)}
          label={p.label}
          variant="primary"
          showArrow={true}
          analyticsId={`${analyticsPrefix}${p.analytics}`}
        />
      {s && (
        <CTAButton
          href={typeof s.href === 'function' ? s.href(baseUrl) : s.href}
          label={s.label}
          variant="secondary"
          showArrow={false}
          analyticsId={`${analyticsPrefix}${s.analytics}`}
        />
      )}
      </div>
      {microcopy && (
        <p className="text-sm text-muted-foreground font-medium text-center">
          {microcopy}
        </p>
      )}
    </div>
  );
}
