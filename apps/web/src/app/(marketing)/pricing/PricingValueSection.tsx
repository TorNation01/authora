'use client';

import { BookOpen, Target, Sparkles, Layout, Scissors, CheckCircle2 } from 'lucide-react';

const HIGHLIGHTS = [
  { icon: BookOpen, text: 'Plan your book with confidence' },
  { icon: Layout, text: 'Write inside a real manuscript workspace' },
  { icon: Sparkles, text: 'Get unstuck with guided AI support' },
  { icon: Target, text: 'Stay accountable with goals and reminders' },
  { icon: Scissors, text: 'Use manuscript intelligence to find what is missing and what should be trimmed' },
  { icon: CheckCircle2, text: 'Finish with structure, not chaos' },
];

export function PricingValueSection() {
  return (
    <section className="py-20" data-analytics="pricing-value">
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
          More than a writing app
        </h2>
        <p className="mt-6 text-muted-foreground leading-relaxed">
          Authora is built to help you do more than collect ideas. It helps you shape them, write
          them, stay accountable to them, strengthen the manuscript, and actually finish it.
        </p>
        <ul className="mt-10 grid gap-4 sm:grid-cols-2">
          {HIGHLIGHTS.map((item) => (
            <li key={item.text} className="flex items-center gap-3 rounded-lg border border-border/60 bg-card p-4 text-left">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <span className="text-sm font-medium text-foreground">{item.text}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
