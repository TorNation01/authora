'use client';

import { Target, Bell, TrendingUp, Flag, Zap } from 'lucide-react';

const FEATURES = [
  { icon: Target, label: 'Writing goals', desc: 'Set and track daily or weekly targets' },
  { icon: TrendingUp, label: 'Streak tracking', desc: 'Build momentum with visible progress' },
  { icon: Bell, label: 'Reminders', desc: 'Gentle nudges to keep you on track' },
  { icon: Flag, label: 'Progress milestones', desc: 'Celebrate chapter and book completions' },
  { icon: Zap, label: 'Finish Mode', desc: 'Focused push to cross the finish line' },
];

export function AccountabilitySection() {
  return (
    <section
      className="py-[var(--section-padding-y)]"
      data-analytics="accountability"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-success/80 mb-4">
            Built to finish
          </p>
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Momentum that helps you actually finish.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Goals, streaks, reminders, milestones, and Finish Mode — designed to keep you moving
            without feeling childish.
          </p>
          <p className="mt-6 font-serif text-lg font-medium text-foreground">
            No more half-finished books.
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
          {FEATURES.map((item) => (
            <div
              key={item.label}
              className="card-premium p-6 text-center"
              data-analytics="accountability-feature"
            >
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-success/15 ring-1 ring-success/20">
                <item.icon className="h-7 w-7 text-success" />
              </div>
              <h3 className="mt-4 font-semibold text-foreground">{item.label}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
