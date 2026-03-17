'use client';

import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

interface PricingHeroProps {
  billingInterval: 'monthly' | 'yearly';
  onBillingIntervalChange: (v: 'monthly' | 'yearly') => void;
}

export function PricingHero({ billingInterval, onBillingIntervalChange }: PricingHeroProps) {
  return (
    <section className="relative overflow-hidden border-b border-white/[0.06]">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/[0.06] via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.08),transparent)]" />

      <div className="relative mx-auto max-w-4xl px-[var(--section-padding-x)] py-16 text-center sm:py-20">
        <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Plans for every kind of writer
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
          Whether you&apos;re outlining your first idea, finishing your next manuscript, or building a
          full writing habit — Authora gives you the tools, structure, and support to keep moving.
        </p>
        <p className="mt-4 font-serif text-base font-medium text-foreground">
          Write with clarity. Stay accountable. Finish what you start.
        </p>

        {/* Monthly / Yearly toggle */}
        <div className="mt-10 flex justify-center">
          <div className="inline-flex rounded-xl border border-white/[0.12] bg-white/[0.03] p-1.5 shadow-[var(--shadow-card-premium)]">
            <button
              type="button"
              onClick={() => onBillingIntervalChange('monthly')}
              className={`rounded-lg px-5 py-2.5 text-sm font-medium transition-all duration-200 ${
                billingInterval === 'monthly'
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Monthly
            </button>
            <button
              type="button"
              onClick={() => onBillingIntervalChange('yearly')}
              className={`rounded-lg px-5 py-2.5 text-sm font-medium transition-all duration-200 ${
                billingInterval === 'yearly'
                  ? 'bg-primary text-primary-foreground shadow-md'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              Yearly
              <span className="ml-2 rounded bg-white/20 px-1.5 py-0.5 text-xs">
                Save up to 25%
              </span>
            </button>
          </div>
        </div>

        <div className="mt-10">
          <CTAPair
            primary="start-free"
            secondary="compare-plans"
            microcopy={CTA_MICROCOPY.pricing}
            analyticsPrefix="pricing-hero-"
          />
        </div>
      </div>
    </section>
  );
}
