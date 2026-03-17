'use client';

import { FileQuestion, FileText, Compass, Brain, Flag } from 'lucide-react';

const THEMES = [
  {
    icon: FileQuestion,
    vs: 'Blank page',
    authora: 'Guided system',
  },
  {
    icon: FileText,
    vs: 'Basic editor',
    authora: 'Full writing studio',
  },
  {
    icon: Compass,
    vs: 'No direction',
    authora: 'Step-by-step flow',
  },
  {
    icon: Brain,
    vs: 'No insight',
    authora: 'Manuscript intelligence',
  },
  {
    icon: Flag,
    vs: 'Easy to start',
    authora: 'Built to finish',
  },
];

export function WhyDifferentSection() {
  return (
    <section className="py-20" data-analytics="why-different">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            This is not just writing software.
          </h2>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {THEMES.map((item) => (
            <div
              key={item.vs}
              className="card-sanctuary flex items-start gap-4 p-6"
              data-analytics="why-different-theme"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground line-through">{item.vs}</p>
                <p className="mt-1 font-medium text-foreground">{item.authora}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
