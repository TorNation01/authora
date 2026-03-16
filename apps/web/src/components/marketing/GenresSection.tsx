'use client';

import { BookOpen, FileText } from 'lucide-react';

const FICTION_GENRES = [
  'Romance',
  'Fantasy',
  'Sci-fi',
  'Thriller',
  'Mystery',
  'Horror',
  'Historical fiction',
  'Literary fiction',
  'Young adult',
  'Short stories and series',
];

const NONFICTION_GENRES = [
  'Memoir',
  'Self-help',
  'Business',
  'Finance',
  'Health and wellness',
  'Parenting',
  'Relationships',
  'Educational books',
  'Thought leadership',
  'Workbooks and guided books',
];

export function GenresSection() {
  return (
    <section className="py-20" data-analytics="genres">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Built for fiction and non-fiction writers
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Authora is flexible enough to support many kinds of books while still giving each
            project the structure it needs.
          </p>
        </div>
        <div className="mt-16 grid gap-8 lg:grid-cols-2">
          <div className="card-sanctuary overflow-hidden p-8" data-analytics="genre-fiction">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <BookOpen className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h3 className="font-serif text-xl font-semibold text-foreground">Fiction</h3>
              </div>
            </div>
            <ul className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {FICTION_GENRES.map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="text-primary">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="card-sanctuary overflow-hidden p-8" data-analytics="genre-nonfiction">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-primary/10">
                <FileText className="h-7 w-7 text-primary" />
              </div>
              <div>
                <h3 className="font-serif text-xl font-semibold text-foreground">Non-fiction</h3>
              </div>
            </div>
            <ul className="mt-6 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {NONFICTION_GENRES.map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span className="text-primary">•</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <p className="mt-10 text-center text-muted-foreground">
          Whether you are writing a novel, a memoir, a workbook, or your first authority book,
          Authora helps you move from idea to finished draft.
        </p>
      </div>
    </section>
  );
}
