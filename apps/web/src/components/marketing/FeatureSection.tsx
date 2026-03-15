'use client';

import { BookOpen, Sparkles, Target, FileDown, PenLine, LayoutGrid } from 'lucide-react';

const FEATURES = [
  {
    icon: BookOpen,
    title: 'Guided planning',
    description: 'Fiction or non-fiction—structured planners and templates help you outline before you write. Romance, thriller, memoir, business: we have you covered.',
  },
  {
    icon: Sparkles,
    title: 'AI when you need it',
    description: 'Stuck? Get suggestions, rewrites, and ideas. AI assists—you stay in control. No overwhelm, just support.',
  },
  {
    icon: Target,
    title: 'Accountability that helps you complete',
    description: 'Goals, reminders, and milestones that feel supportive. Finish your book with gentle nudges, not guilt.',
  },
  {
    icon: FileDown,
    title: 'Export ready',
    description: 'DOCX, PDF, EPUB. One click to share, query, or publish. Your manuscript, ready when you are.',
  },
  {
    icon: PenLine,
    title: 'Writing studio',
    description: 'Distraction-free editor, version history, notes, and research—all in one place. Write without tab chaos.',
  },
  {
    icon: LayoutGrid,
    title: 'All your tools in one place',
    description: 'Outline, draft, revise, export. No more juggling apps. One workspace for your entire book.',
  },
];

export function FeatureSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="features">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Everything you need to finish your book
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            From first idea to final manuscript—guided, supported, and complete.
          </p>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="card-sanctuary p-6 transition-shadow hover:shadow-md"
              data-analytics="feature-card"
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
