'use client';

import { Lightbulb, LayoutTemplate, PenLine, FileCheck, ArrowRight } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

const STEPS = [
  {
    icon: Lightbulb,
    title: 'Start with clarity',
    body: 'Choose what you\'re writing and how much guidance you want.',
  },
  {
    icon: LayoutTemplate,
    title: 'Build your structure',
    body: 'Use templates or go freeform. Authora adapts to you.',
  },
  {
    icon: PenLine,
    title: 'Write with support',
    body: 'Stay in flow with AI assistance, notes, and a clean editor.',
  },
  {
    icon: FileCheck,
    title: 'Finish with confidence',
    body: 'Fix what\'s missing, tighten what\'s weak, and export cleanly.',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="how-it-works"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            How Authora works
          </h2>
          <p className="mt-4 text-muted-foreground">
            Four steps from idea to finished manuscript.
          </p>
        </div>

        <div className="mt-12 flex justify-center">
          <CTAPair
            primary="create-first-book"
            secondary="explore-features"
            microcopy={CTA_MICROCOPY.heroAlt}
            analyticsPrefix="how-it-works-"
          />
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <div
              key={step.title}
              className="relative flex flex-col"
              data-analytics="how-step"
            >
              <div className="flex items-start gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/20">
                  <step.icon className="h-6 w-6 text-primary" />
                </div>
                <span className="text-sm font-medium text-primary/80">Step {i + 1}</span>
              </div>
              <div className="mt-4">
                <h3 className="font-serif text-xl font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-muted-foreground leading-relaxed">{step.body}</p>
              </div>
              {i < STEPS.length - 1 && (
                <div className="absolute -right-4 top-8 hidden text-muted-foreground/30 lg:block">
                  <ArrowRight className="h-5 w-5" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
