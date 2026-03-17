'use client';

import { BookOpen, FileText, User, BookMarked, PenLine, Sparkles, Award } from 'lucide-react';

const USE_CASES = [
  {
    icon: BookOpen,
    title: 'Fiction writers',
    copy: 'Novels, series, short stories. Structure, character arcs, and story intelligence.',
  },
  {
    icon: FileText,
    title: 'Non-fiction writers',
    copy: 'Business, self-help, how-to. Clear structure and research support.',
  },
  {
    icon: User,
    title: 'Memoir writers',
    copy: 'Turn your story into a book with guided structure and reflection tools.',
  },
  {
    icon: BookMarked,
    title: 'Workbook creators',
    copy: 'Templates, exercises, and export for interactive or print formats.',
  },
  {
    icon: PenLine,
    title: 'Ghostwriters',
    copy: 'Client projects, multiple books, professional workflow and export.',
  },
  {
    icon: Sparkles,
    title: 'First-time authors',
    copy: 'Step-by-step guidance from idea to finished manuscript.',
  },
  {
    icon: Award,
    title: 'Experienced authors',
    copy: 'Power tools, flexibility, and manuscript intelligence without hand-holding.',
  },
];

export function UseCasesSection() {
  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="use-cases">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Built for every kind of writer.
          </h2>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {USE_CASES.map((item) => (
            <div
              key={item.title}
              className="card-sanctuary flex items-start gap-4 p-6"
              data-analytics="use-case"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <item.icon className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground">{item.title}</h3>
                <p className="mt-1 text-sm text-muted-foreground">{item.copy}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
