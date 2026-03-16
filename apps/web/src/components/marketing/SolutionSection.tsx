'use client';

import { BookOpen, PenLine, Sparkles, Target, TrendingUp, CheckCircle } from 'lucide-react';

const FEATURES = [
  {
    icon: BookOpen,
    title: 'Plan your book with structure',
    description: 'Shape your ideas and organize chapters with guided planning for fiction or non-fiction.',
  },
  {
    icon: PenLine,
    title: 'Write inside a focused manuscript editor',
    description: 'Draft comfortably in a real writing workspace built for book-length work.',
  },
  {
    icon: Sparkles,
    title: 'Get unstuck with guided AI support',
    description: 'Use AI when you need help with flow, ideas, or structure—without losing your voice.',
  },
  {
    icon: Target,
    title: 'Stay accountable with goals, reminders, and progress tracking',
    description: 'Set goals, receive reminders, and track your progress so you keep moving.',
  },
  {
    icon: TrendingUp,
    title: 'Build momentum with streaks, milestones, and completion tools',
    description: 'Celebrate progress and use Finish Mode to close the gap between starting and finishing.',
  },
  {
    icon: CheckCircle,
    title: 'Finish with clarity instead of chaos',
    description: 'Polish your manuscript, organize your work, and export when you are ready.',
  },
];

export function SolutionSection() {
  return (
    <section className="py-20" data-analytics="solution">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            A writing studio designed to move your book forward
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Authora gives you a guided system for writing, not just an empty document. Shape your
            ideas, organize your chapters, write inside a real manuscript workspace, get help when
            you are stuck, and keep your progress moving with reminders, milestones, and finishing
            tools.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="card-sanctuary p-6 transition-shadow hover:shadow-md"
              data-analytics="solution-feature"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <feature.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
