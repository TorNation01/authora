'use client';

import { Target, Zap } from 'lucide-react';

export function PricingAccountabilitySection() {
  return (
    <section className="py-20 border-t border-border/60" data-analytics="pricing-accountability">
      <div className="mx-auto max-w-2xl text-center">
        <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10">
          <Target className="h-7 w-7 text-primary" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
          Built to help you finish
        </h2>
        <p className="mt-6 text-muted-foreground leading-relaxed">
          Many people dream about writing a book. Far fewer finish one. Authora is designed to close
          that gap with goals, reminders, milestones, progress tracking, and Finish Mode.
        </p>
        <p className="mt-6 flex items-center justify-center gap-2 font-serif text-lg font-medium text-foreground">
          <Zap className="h-5 w-5 text-primary" />
          Because finishing matters.
        </p>
      </div>
    </section>
  );
}
