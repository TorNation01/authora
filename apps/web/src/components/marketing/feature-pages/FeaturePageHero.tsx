'use client';

import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

interface FeaturePageHeroProps {
  title: string;
  subtitle?: string;
  supporting?: string;
  eyebrow?: string;
  showCTA?: boolean;
  ctaMicrocopy?: string;
  primaryOnly?: boolean;
}

export function FeaturePageHero({
  title,
  subtitle,
  supporting,
  eyebrow,
  showCTA = true,
  ctaMicrocopy = CTA_MICROCOPY.heroAlt,
  primaryOnly = false,
}: FeaturePageHeroProps) {
  return (
    <section className="relative overflow-hidden border-b border-white/[0.06]">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/[0.06] via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.08),transparent)]" />

      <div className="relative mx-auto max-w-4xl px-[var(--section-padding-x)] py-16 text-center sm:py-20">
        {eyebrow && (
          <p className="text-sm font-medium uppercase tracking-wider text-primary/80 mb-6">
            {eyebrow}
          </p>
        )}
        <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          {title}
        </h1>
        {subtitle && (
          <p className="mt-4 font-serif text-xl font-medium text-primary">{subtitle}</p>
        )}
        {supporting && (
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
            {supporting}
          </p>
        )}

        {showCTA && (
          <div className="mt-10">
            <CTAPair
              primary="start-writing-free"
              secondary={primaryOnly ? undefined : 'view-pricing'}
              microcopy={ctaMicrocopy}
              analyticsPrefix="feature-hero-"
            />
          </div>
        )}
      </div>
    </section>
  );
}
