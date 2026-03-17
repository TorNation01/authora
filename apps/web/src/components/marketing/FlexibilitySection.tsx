'use client';

import { BookOpen, Layers, FileText, PenLine, Compass } from 'lucide-react';

const FLEXIBILITY_POINTS = [
  { icon: BookOpen, text: 'Multiple books at once' },
  { icon: Layers, text: 'Different modes per project' },
  { icon: FileText, text: 'Fiction + non-fiction + hybrid' },
  { icon: Compass, text: 'Guided, flexible, or freeform' },
  { icon: PenLine, text: 'Templates or blank starts' },
];

export function FlexibilitySection() {
  return (
    <section
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="flexibility"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Write one book — or ten.
          </h2>
          <p className="mt-4 text-muted-foreground">
            Adaptable to your workflow. Freedom without chaos.
          </p>
        </div>

        <div className="mt-12 flex flex-wrap justify-center gap-4">
          {FLEXIBILITY_POINTS.map((item, i) => (
            <div
              key={i}
              className="card-premium flex items-center gap-3 px-6 py-4"
              data-analytics="flexibility-point"
            >
              <item.icon className="h-5 w-5 text-primary shrink-0" />
              <span className="font-medium text-foreground">{item.text}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
