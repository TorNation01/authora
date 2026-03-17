'use client';

import { Check } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY, CTA_TRUST_BADGES } from '@/content/cta-copy';

const PLANS = [
  { name: 'Free', highlight: 'Start here' },
  { name: 'Starter', highlight: null },
  { name: 'Pro', highlight: 'Most popular' },
  { name: 'Studio', highlight: null },
];

export function PricingTeaserSection() {
  return (
    <section
      className="py-[var(--section-padding-y)]"
      data-analytics="pricing-teaser"
    >
      <div className="mx-auto max-w-4xl px-[var(--section-padding-x)]">
        <div className="rounded-2xl border border-white/[0.08] bg-gradient-to-b from-primary/5 to-transparent p-8 sm:p-12">
          <div className="text-center">
            <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
              Start free. Upgrade when you&apos;re ready.
            </h2>
            <p className="mt-4 text-muted-foreground">
              {CTA_MICROCOPY.pricingTeaserAlt}
            </p>

            <div className="mt-8 flex flex-wrap justify-center gap-3">
              {PLANS.map((plan) => (
                <div
                  key={plan.name}
                  className="flex items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.02] px-4 py-2"
                >
                  <span className="font-medium text-foreground">{plan.name}</span>
                  {plan.highlight && (
                    <span className="rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary">
                      {plan.highlight}
                    </span>
                  )}
                </div>
              ))}
            </div>

            <div className="mt-8">
              <CTAPair
                primary="start-writing-free"
                secondary="view-full-pricing"
                microcopy={CTA_MICROCOPY.pricingTeaser}
                analyticsPrefix="pricing-teaser-"
              />
            </div>

            <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm text-muted-foreground">
              {CTA_TRUST_BADGES.map((badge) => (
                <span key={badge} className="flex items-center gap-2">
                  <Check className="h-4 w-4 text-success" />
                  {badge}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
