'use client';

import { BookOpen, Layers, FileText, PenLine } from 'lucide-react';

const FLEXIBILITY_POINTS = [
  { icon: BookOpen, text: 'Multiple books at once' },
  { icon: Layers, text: 'Different modes per project' },
  { icon: FileText, text: 'Fiction + non-fiction + hybrid' },
  { icon: PenLine, text: 'Templates or blank starts' },
  { icon: PenLine, text: 'Adaptable to your writing style' },
];

export function FlexibilitySection() {
  return (
    <section className="py-20" data-analytics="flexibility">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Write one book — or ten.
          </h2>
        </div>
        <div className="mt-12 flex flex-wrap justify-center gap-6">
          {FLEXIBILITY_POINTS.map((item, i) => (
            <div
              key={i}
              className="flex items-center gap-3 rounded-lg border border-border/60 bg-card px-5 py-3"
              data-analytics="flexibility-point"
            >
              <item.icon className="h-5 w-5 text-primary shrink-0" />
              <span className="text-sm font-medium text-foreground">{item.text}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
