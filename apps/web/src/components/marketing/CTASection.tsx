'use client';

import { PenLine } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

export function CTASection() {
  return (
    <section
      className="relative overflow-hidden py-[var(--section-padding-y)]"
      data-analytics="cta"
    >
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/[0.04] to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />

      <div className="relative mx-auto max-w-4xl px-[var(--section-padding-x)] text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary/90 mb-8">
          <PenLine className="h-4 w-4" />
          Your next chapter starts here
        </div>

        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl">
          Your book isn&apos;t finished yet — but it can be.
        </h2>
        <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
          Authora gives you the tools, structure, and support to get there.
        </p>

        <div className="mt-10 flex flex-col items-center">
          <CTAPair
            primary="start-writing-free"
            secondary="create-first-book"
            microcopy={CTA_MICROCOPY.ctaSection}
            analyticsPrefix="cta-final-"
          />
        </div>
      </div>
    </section>
  );
}
