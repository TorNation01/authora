'use client';

import { FileText, Sparkles, Lightbulb, FileEdit } from 'lucide-react';

const WRITING_STUDIO = ['Clean manuscript editor', 'Chapter and section control', 'Notes, comments, highlights'];

const AI_ASSISTANCE = ['Brainstorming', 'Rewriting', 'Clarity improvement', 'Idea generation'];

const RESEARCH_IDEAS = ['Idea capture', 'Research vault', 'Character and world tracking'];

const REVISION_TOOLS = ['Revision passes', 'Issue tracking', 'Structured improvement flow'];

const CARDS = [
  { icon: FileText, title: 'Writing Studio', items: WRITING_STUDIO },
  { icon: Sparkles, title: 'AI Assistance', items: AI_ASSISTANCE },
  { icon: Lightbulb, title: 'Research & Ideas', items: RESEARCH_IDEAS },
  { icon: FileEdit, title: 'Revision Tools', items: REVISION_TOOLS },
];

export function WritingExperienceSection() {
  return (
    <section
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="writing-experience"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Everything you need — in one place.
          </h2>
          <p className="mt-4 text-muted-foreground">
            A complete writing environment built for book-length work.
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {CARDS.map((card) => (
            <div
              key={card.title}
              className="card-premium p-6"
              data-analytics={`writing-${card.title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/20 mb-5">
                <card.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold text-foreground text-lg">{card.title}</h3>
              <ul className="mt-3 space-y-2">
                {card.items.map((item) => (
                  <li key={item} className="text-sm text-muted-foreground flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary/50" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
