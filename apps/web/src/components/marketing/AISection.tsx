'use client';

import { RefreshCw, Expand, Lightbulb, Sparkles, FileEdit, Bot } from 'lucide-react';

const AI_SUPPORT_EXAMPLES = [
  { icon: RefreshCw, label: 'Rewrite awkward passages' },
  { icon: Expand, label: 'Expand thin sections' },
  { icon: Lightbulb, label: 'Generate ideas when stuck' },
  { icon: Sparkles, label: 'Improve flow and clarity' },
  { icon: FileEdit, label: 'Turn outlines into rough drafts' },
  { icon: Bot, label: 'Use ghostwriter-style assistance when needed' },
];

export function AISection() {
  return (
    <section className="py-20" data-analytics="ai">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            AI that helps without taking over
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Use AI when you want support with flow, clarity, wording, idea generation, structure, or
            getting unstuck. Stay in control of your voice and your vision while Authora helps you
            keep moving.
          </p>
        </div>
        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {AI_SUPPORT_EXAMPLES.map((item) => (
            <div
              key={item.label}
              className="card-sanctuary flex items-center gap-4 p-4"
              data-analytics="ai-example"
            >
              <item.icon className="h-5 w-5 shrink-0 text-primary" />
              <span className="text-sm text-foreground">{item.label}</span>
            </div>
          ))}
        </div>
        <p className="mt-10 text-center font-medium text-foreground">
          Your voice stays at the center.
        </p>
      </div>
    </section>
  );
}
