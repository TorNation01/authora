'use client';

import { Lightbulb, LayoutTemplate, PenLine, TrendingUp, FileCheck } from 'lucide-react';

const STEPS = [
  {
    icon: Lightbulb,
    title: 'Start with your idea',
    body: 'Capture your concept, choose your book type, and build a clear starting point for your project.',
  },
  {
    icon: LayoutTemplate,
    title: 'Shape the structure',
    body: 'Use guided planning tools for fiction or non-fiction to organize chapters, themes, sections, research, and ideas.',
  },
  {
    icon: PenLine,
    title: 'Write with support',
    body: "Draft inside Authora's writing studio with editor tools, notes, smart prompts, and AI help available when you need it.",
  },
  {
    icon: TrendingUp,
    title: 'Keep your momentum',
    body: 'Use goals, reminders, streaks, milestones, and Finish Mode to stay accountable and keep moving.',
  },
  {
    icon: FileCheck,
    title: 'Finish and prepare',
    body: 'Polish your manuscript, organize your work, and export it when you are ready for the next stage.',
  },
];

export function HowItWorksSection() {
  return (
    <section
      id="how-it-works"
      className="border-t border-border/60 bg-muted/30 py-20"
      data-analytics="how-it-works"
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            How Authora works
          </h2>
        </div>
        <div className="mt-16 space-y-12">
          {STEPS.map((step, i) => (
            <div
              key={step.title}
              className="flex flex-col gap-6 sm:flex-row sm:items-start"
              data-analytics="how-step"
            >
              <div className="flex shrink-0 items-center gap-4 sm:w-64">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                  <step.icon className="h-6 w-6 text-primary" />
                </div>
                <span className="text-sm font-medium text-muted-foreground">Step {i + 1}</span>
              </div>
              <div className="flex-1">
                <h3 className="font-serif text-xl font-semibold text-foreground">{step.title}</h3>
                <p className="mt-2 text-muted-foreground leading-relaxed">{step.body}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
