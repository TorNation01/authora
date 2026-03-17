'use client';

import { Lightbulb, LayoutTemplate, PenLine, FileCheck } from 'lucide-react';

const STEPS = [
  {
    icon: Lightbulb,
    title: 'Start with clarity',
    body: 'Choose what you are writing and how much guidance you want.',
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
    body: 'Fix what is missing, tighten what is weak, and export cleanly.',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="border-t border-border/60 bg-muted/30 py-20"
      data-analytics="how-it-works"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            How Authora works
          </h2>
        </div>
        <div className="mt-16 grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((step, i) => (
            <div
              key={step.title}
              className="flex flex-col gap-4"
              data-analytics="how-step"
            >
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <step.icon className="h-6 w-6 text-primary" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Step {i + 1}</span>
              </div>
              <div>
                <h3 className="font-serif text-xl font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-muted-foreground leading-relaxed">{step.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
