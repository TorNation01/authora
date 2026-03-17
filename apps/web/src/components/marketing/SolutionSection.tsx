'use client';

import { BookOpen, PenLine, Sparkles, Target, TrendingUp, FileCheck } from 'lucide-react';

const PILLARS = [
  { icon: BookOpen, label: 'Guided or flexible writing paths' },
  { icon: PenLine, label: 'Full manuscript editor' },
  { icon: Sparkles, label: 'AI writing assistance' },
  { icon: Target, label: 'Built-in accountability' },
  { icon: TrendingUp, label: 'Smart revision system' },
  { icon: FileCheck, label: 'Clean export for real-world use' },
];

export function SolutionSection() {
  return (
    <section className="py-20" data-analytics="solution">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            A complete writing system — not just a blank page.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Authora combines writing tools, AI assistance, structure, and momentum into one seamless experience.
          </p>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {PILLARS.map((item) => (
            <div
              key={item.label}
              className="card-sanctuary flex items-center gap-4 p-6 transition-shadow hover:shadow-md"
              data-analytics="solution-feature"
            >
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                <item.icon className="h-6 w-6 text-primary" />
              </div>
              <p className="font-medium text-foreground">{item.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
