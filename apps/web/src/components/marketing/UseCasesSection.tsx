'use client';

import Link from 'next/link';
import { BookOpen, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';

const FICTION_BULLETS = [
  'Genre templates: romance, thriller, fantasy, mystery',
  'Scene and chapter planning',
  'Character and worldbuilding tools',
  'Ghostwriter mode for AI-assisted drafting',
  'Export for querying or self-publishing',
];

const NONFICTION_BULLETS = [
  'Templates: memoir, business, self-help, educational',
  'Problem–solution–implementation structure',
  'Target audience and transformation framing',
  'Research notes and citations',
  'Export for traditional or indie publishing',
];

export function UseCasesSection() {
  return (
    <section className="py-20" data-analytics="use-cases">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Fiction or non-fiction—we've got you
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Purpose-built templates and workflows for your genre.
          </p>
        </div>
        <div className="mt-16 grid gap-8 lg:grid-cols-2">
          {/* Fiction */}
          <div
            className="card-sanctuary overflow-hidden p-8"
            data-analytics="use-case-fiction"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <BookOpen className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h3 className="font-serif text-xl font-semibold text-foreground">
                  Fiction writers
                </h3>
                <p className="text-sm text-muted-foreground">
                  Novels, stories, series
                </p>
              </div>
            </div>
            <ul className="mt-6 space-y-3">
              {FICTION_BULLETS.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <span className="mt-1 text-primary">•</span>
                  {item}
                </li>
              ))}
            </ul>
            {/* Placeholder for fiction screenshot */}
            <div className="mt-8 aspect-video rounded-lg bg-muted/50 flex items-center justify-center">
              <p className="text-xs text-muted-foreground">Fiction workspace preview</p>
            </div>
          </div>
          {/* Nonfiction */}
          <div
            className="card-sanctuary overflow-hidden p-8"
            data-analytics="use-case-nonfiction"
          >
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <FileText className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h3 className="font-serif text-xl font-semibold text-foreground">
                  Non-fiction authors
                </h3>
                <p className="text-sm text-muted-foreground">
                  Memoir, business, how-to, thought leadership
                </p>
              </div>
            </div>
            <ul className="mt-6 space-y-3">
              {NONFICTION_BULLETS.map((item) => (
                <li key={item} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <span className="mt-1 text-primary">•</span>
                  {item}
                </li>
              ))}
            </ul>
            {/* Placeholder for nonfiction screenshot */}
            <div className="mt-8 aspect-video rounded-lg bg-muted/50 flex items-center justify-center">
              <p className="text-xs text-muted-foreground">Non-fiction workspace preview</p>
            </div>
          </div>
        </div>
        <div className="mt-12 text-center">
          <Button asChild variant="outline">
            <Link href="/features">See all features</Link>
          </Button>
        </div>
      </div>
    </section>
  );
}
