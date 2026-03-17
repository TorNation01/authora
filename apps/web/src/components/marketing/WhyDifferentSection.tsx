'use client';

import { FileQuestion, FileText, Compass, Brain, Flag } from 'lucide-react';

const THEMES = [
  { icon: FileQuestion, vs: 'Blank page', authora: 'Guided system' },
  { icon: FileText, vs: 'Basic editor', authora: 'Full writing studio' },
  { icon: Compass, vs: 'No direction', authora: 'Step-by-step flow' },
  { icon: Brain, vs: 'No insight', authora: 'Manuscript intelligence' },
  { icon: Flag, vs: 'Easy to start', authora: 'Built to finish' },
];

export function WhyDifferentSection() {
  return (
    <section
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="why-different"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            This is not just writing software.
          </h2>
          <p className="mt-4 text-muted-foreground">
            A clear contrast between the old way and the Authora way.
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {THEMES.map((item) => (
            <div
              key={item.vs}
              className="card-premium flex items-start gap-4 p-6"
              data-analytics="why-different-theme"
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/20">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-muted-foreground line-through">{item.vs}</p>
                <p className="mt-1 font-semibold text-foreground">{item.authora}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
