'use client';

import { Brain } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';

export function EnginesCombinedSection() {
  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-b from-primary/10 via-transparent to-transparent transition-all duration-300 hover:border-primary/20"
      data-analytics="engines-combined"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />
      <div className="relative mx-auto max-w-4xl px-8 py-16 text-center sm:px-12 sm:py-20">
        <div className="mx-auto mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/15 ring-1 ring-primary/20">
          <Brain className="h-7 w-7 text-primary" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl lg:text-4xl">
          Not just writing tools — writing intelligence.
        </h2>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
          Most tools give you a blank page. Authora gives you a system that helps you write,
          strengthen, and finish the manuscript properly.
        </p>
        <p className="mt-8 font-serif text-xl font-semibold text-foreground">
          Write better. Revise faster. Finish stronger.
        </p>
        <div className="mt-10 flex justify-center">
          <CTAPair
            primary="start-writing-free"
            secondary="view-pricing"
            analyticsPrefix="engines-combined-"
          />
        </div>
      </div>
    </section>
  );
}
