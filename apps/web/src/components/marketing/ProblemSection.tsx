'use client';

import { Heart, BookOpen, Repeat, HelpCircle, Target, XCircle } from 'lucide-react';

const PAIN_POINTS = [
  { icon: BookOpen, text: 'You don\'t know where to start' },
  { icon: Repeat, text: 'You start, then lose momentum' },
  { icon: HelpCircle, text: 'You get stuck in the middle' },
  { icon: Repeat, text: 'You rewrite the same chapters over and over' },
  { icon: Target, text: 'Something feels off, but you don\'t know what' },
  { icon: XCircle, text: 'You never actually finish' },
];

export function ProblemSection() {
  return (
    <section
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="problem"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-3xl text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary/90 mb-6">
            <Heart className="h-4 w-4" />
            We get it
          </div>
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Most people don&apos;t fail because they can&apos;t write.
          </h2>
          <p className="mt-6 text-lg text-muted-foreground leading-relaxed">
            They fail because writing a book becomes overwhelming.
          </p>
        </div>

        <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 max-w-5xl mx-auto">
          {PAIN_POINTS.map((point) => (
            <div
              key={point.text}
              className="group flex items-start gap-4 rounded-xl border border-white/[0.06] bg-white/[0.02] p-5 transition-all duration-300 hover:border-white/[0.1] hover:bg-white/[0.04]"
              data-analytics="problem-point"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-muted/50 text-muted-foreground group-hover:text-primary/80 transition-colors">
                <point.icon className="h-5 w-5" />
              </div>
              <p className="text-muted-foreground leading-relaxed">{point.text}</p>
            </div>
          ))}
        </div>

        <p className="mt-12 text-center font-serif text-lg font-medium text-foreground">
          Authora solves all of that in one place.
        </p>
      </div>
    </section>
  );
}
