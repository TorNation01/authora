'use client';

import { useConfig } from '@/contexts/ConfigProvider';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

export function PricingFinalCTA() {
  const { feature_flags } = useConfig();
  if (!feature_flags.standalone_auth) return null;

  return (
    <section
      className="relative overflow-hidden border-t border-white/[0.06] py-[var(--section-padding-y)]"
      data-analytics="pricing-final-cta"
    >
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.04] to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />

      <div className="relative mx-auto max-w-3xl px-[var(--section-padding-x)] text-center">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Ready to finish your book?
        </h2>
        <p className="mt-6 text-lg text-muted-foreground">
          Start free. Upgrade when you&apos;re ready. No credit card required.
        </p>

        <div className="mt-10 flex flex-col items-center">
          <CTAPair
            primary="start-free"
            secondary="compare-plans"
            microcopy={CTA_MICROCOPY.pricingFinal}
            analyticsPrefix="pricing-final-"
          />
        </div>
      </div>
    </section>
  );
}
