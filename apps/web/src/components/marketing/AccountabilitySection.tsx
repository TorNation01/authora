'use client';

import { Target, Bell, TrendingUp, Flag, Zap } from 'lucide-react';

export function AccountabilitySection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="accountability">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Built to help you finish
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Authora is designed for more than inspiration. It is designed for completion. With
            writing goals, milestones, reminders, progress tracking, streaks, and Finish Mode, the
            platform helps close the gap between wanting to write a book and actually finishing one.
          </p>
          <p className="mt-6 font-serif text-lg font-medium text-foreground">
            Because a finished book changes everything.
          </p>
        </div>
        <div className="mt-12 flex flex-wrap justify-center gap-6">
          <div className="flex items-center gap-3 text-muted-foreground">
            <Target className="h-5 w-5 text-primary" />
            <span>Writing goals</span>
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <Bell className="h-5 w-5 text-primary" />
            <span>Reminders</span>
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <TrendingUp className="h-5 w-5 text-primary" />
            <span>Progress tracking</span>
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <Flag className="h-5 w-5 text-primary" />
            <span>Milestones</span>
          </div>
          <div className="flex items-center gap-3 text-muted-foreground">
            <Zap className="h-5 w-5 text-primary" />
            <span>Finish Mode</span>
          </div>
        </div>
      </div>
    </section>
  );
}
