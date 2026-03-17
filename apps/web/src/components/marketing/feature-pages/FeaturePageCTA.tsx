'use client';

import Link from 'next/link';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

interface FeaturePageCTAProps {
  headline?: string;
  supporting?: string;
  /** Optional link below supporting text (e.g. View pricing) */
  supportingLink?: { href: string; label: string };
  primary?: 'start-writing-free' | 'start-free' | 'create-first-book';
  secondary?: 'view-pricing' | 'explore-features' | null;
  microcopy?: string;
  analyticsPrefix?: string;
  variant?: 'default' | 'accent';
  primaryOnly?: boolean;
}

export function FeaturePageCTA({
  headline = 'Ready to finish your book?',
  supporting = 'Start free. Upgrade when you\'re ready.',
  supportingLink,
  primary = 'start-writing-free',
  secondary = 'view-pricing',
  microcopy = CTA_MICROCOPY.ctaSection,
  analyticsPrefix = 'feature-cta-',
  variant = 'default',
  primaryOnly = false,
}: FeaturePageCTAProps) {
  return (
    <section
      className={`relative overflow-hidden border-t border-white/[0.06] py-[var(--section-padding-y)] ${
        variant === 'accent' ? 'bg-gradient-to-b from-transparent via-primary/[0.04] to-transparent' : ''
      }`}
    >
      {variant === 'accent' && (
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />
      )}
      <div className="relative mx-auto max-w-3xl px-[var(--section-padding-x)] text-center">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          {headline}
        </h2>
        {supporting && (
          <p className="mt-6 text-lg text-muted-foreground">{supporting}</p>
        )}
        {supportingLink && (
          <p className="mt-3">
            <Link
              href={supportingLink.href}
              className="text-sm font-medium text-primary hover:underline"
              data-analytics={`${analyticsPrefix}supporting-link`}
            >
              {supportingLink.label}
            </Link>
          </p>
        )}
        <div className="mt-10 flex flex-col items-center">
          <CTAPair
            primary={primary}
            secondary={primaryOnly ? undefined : secondary ?? undefined}
            microcopy={microcopy}
            analyticsPrefix={analyticsPrefix}
          />
        </div>
      </div>
    </section>
  );
}
