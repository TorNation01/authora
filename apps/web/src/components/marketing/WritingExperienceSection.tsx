'use client';

import { FileText, Sparkles, Lightbulb, FileEdit } from 'lucide-react';

const WRITING_STUDIO = [
  'Clean manuscript editor',
  'Chapter and section control',
  'Notes, comments, highlights',
];

const AI_ASSISTANCE = [
  'Brainstorming',
  'Rewriting',
  'Clarity improvement',
  'Idea generation',
];

const RESEARCH_IDEAS = [
  'Idea capture',
  'Research vault',
  'Character and world tracking',
];

const REVISION_TOOLS = [
  'Revision passes',
  'Issue tracking',
  'Structured improvement flow',
];

export function WritingExperienceSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="writing-experience">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Everything you need — in one place.
          </h2>
        </div>
        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="card-sanctuary p-6" data-analytics="writing-studio">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 mb-4">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground">Writing Studio</h3>
            <ul className="mt-3 space-y-2">
              {WRITING_STUDIO.map((item) => (
                <li key={item} className="text-sm text-muted-foreground">• {item}</li>
              ))}
            </ul>
          </div>
          <div className="card-sanctuary p-6" data-analytics="ai-assistance">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 mb-4">
              <Sparkles className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground">AI Assistance</h3>
            <ul className="mt-3 space-y-2">
              {AI_ASSISTANCE.map((item) => (
                <li key={item} className="text-sm text-muted-foreground">• {item}</li>
              ))}
            </ul>
          </div>
          <div className="card-sanctuary p-6" data-analytics="research-ideas">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 mb-4">
              <Lightbulb className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground">Research and Ideas</h3>
            <ul className="mt-3 space-y-2">
              {RESEARCH_IDEAS.map((item) => (
                <li key={item} className="text-sm text-muted-foreground">• {item}</li>
              ))}
            </ul>
          </div>
          <div className="card-sanctuary p-6" data-analytics="revision-tools">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 mb-4">
              <FileEdit className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-foreground">Revision Tools</h3>
            <ul className="mt-3 space-y-2">
              {REVISION_TOOLS.map((item) => (
                <li key={item} className="text-sm text-muted-foreground">• {item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
