'use client';

import { Target, Bell, TrendingUp, Flag, Zap } from 'lucide-react';

const FEATURES = [
  { icon: Target, label: 'Writing goals' },
  { icon: TrendingUp, label: 'Streak tracking' },
  { icon: Bell, label: 'Reminders' },
  { icon: Flag, label: 'Progress milestones' },
  { icon: Zap, label: 'Finish Mode' },
];

export function AccountabilitySection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="accountability">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Built to help you actually finish.
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Writing goals, streak tracking, reminders, progress milestones, Finish Mode.
          </p>
          <p className="mt-6 font-serif text-lg font-medium text-foreground">
            No more half-finished books.
          </p>
        </div>
        <div className="mt-12 flex flex-wrap justify-center gap-6">
          {FEATURES.map((item) => (
            <div key={item.label} className="flex items-center gap-3 text-muted-foreground">
              <item.icon className="h-5 w-5 text-primary" />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
