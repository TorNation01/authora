'use client';

import Link from 'next/link';
import { CTAPair } from '@/components/public/CTAPair';
import { ArrowRight } from 'lucide-react';
import {
  BookOpen,
  FileText,
  Library,
  CheckCircle2,
  Link2,
  ListOrdered,
} from 'lucide-react';

const FEATURES = [
  { icon: Library, label: 'Source library — add and manage references' },
  { icon: Link2, label: 'In-text citations — APA, MLA, Chicago, Harvard' },
  { icon: ListOrdered, label: 'Bibliography generation — formatted output' },
  { icon: FileText, label: 'Zotero integration — sync your library' },
  { icon: BookOpen, label: 'Academic templates — essays, exams, courses, and lecture materials' },
  { icon: CheckCircle2, label: 'CSL-based — industry-standard citation styles' },
];

export function CitationReferenceEngineSection() {
  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-white/[0.08] bg-gradient-to-br from-card via-card to-primary/5 transition-all duration-300 hover:border-primary/20 hover:shadow-glow-gold-subtle"
      data-analytics="citation-reference-engine"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_100%_100%,hsl(var(--primary)/0.08),transparent)]" />
      <div className="relative p-8 sm:p-10 lg:p-12">
        <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 ring-1 ring-primary/20">
              <BookOpen className="h-8 w-8 text-primary" />
            </div>
            <p className="text-sm font-medium uppercase tracking-wider text-primary/90">
              Citation & Reference Engine™
            </p>
            <h2 className="mt-2 font-serif text-2xl font-bold text-foreground sm:text-3xl">
              Cite with confidence. Build your bibliography.
            </h2>
            <p className="mt-4 max-w-xl text-muted-foreground leading-relaxed">
              Add sources to your vault, insert in-text citations, and generate formatted
              bibliographies. APA, MLA, Chicago, Harvard, IEEE — plus Zotero sync for
              students, teachers, lecturers, researchers, and academics.
            </p>
            <p className="mt-6 font-serif text-lg font-medium text-foreground">
              Research-backed writing. Properly cited. Export-ready.
            </p>
            <ul className="mt-8 space-y-4">
              {FEATURES.map((item) => (
                <li key={item.label} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <item.icon className="h-3 w-3 text-primary" />
                  </div>
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8 rounded-xl border border-white/[0.06] bg-white/[0.02] p-5">
              <p className="flex items-start gap-3 text-sm text-muted-foreground">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                <span>
                  Built for students, teachers, lecturers, researchers, and academic writers.
                  No more manual formatting — Authora handles the style.
                </span>
              </p>
            </div>
          </div>
          <div className="flex shrink-0 flex-col items-start gap-4 lg:min-w-[200px]">
            <Link
              href="/citation-reference-engine"
              className="text-sm font-medium text-primary hover:underline inline-flex items-center gap-1"
            >
              Learn more about Citation & Reference Engine
              <ArrowRight className="h-4 w-4" />
            </Link>
            <CTAPair
              primary="start-writing-free"
              secondary="view-pricing"
              analyticsPrefix="citation-reference-"
              className="items-start"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
