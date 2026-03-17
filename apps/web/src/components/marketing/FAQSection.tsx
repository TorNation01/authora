'use client';

import { useState } from 'react';
import Link from 'next/link';

const FAQ_ITEMS = [
  {
    q: 'Is Authora only for fiction writers?',
    a: 'No. Authora supports fiction, non-fiction, memoir, workbooks, and more. Built for every kind of writer.',
  },
  {
    q: 'Does Authora include a real editor?',
    a: 'Yes. Authora includes a full manuscript editor designed for book-length writing, with chapters, notes, and revision tools.',
  },
  {
    q: 'Can Authora help when I get stuck?',
    a: 'Yes. AI assistance for brainstorming, rewriting, clarity, and idea generation. Plus structure guidance and manuscript intelligence.',
  },
  {
    q: 'Can I use Authora for more than one book?',
    a: 'Yes. Work on multiple books at once. Different modes and templates per project.',
  },
  {
    q: 'Will Authora write the book for me?',
    a: 'You stay in control. Use AI as much or as little as you want—from light support to ghostwriter-style assistance.',
  },
  {
    q: 'Do I need to be a professional writer?',
    a: 'No. Authora is built for first-time authors and experienced writers alike.',
  },
];

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);
  return (
    <section className="py-20" data-analytics="faq">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-muted-foreground">
            Everything you need to know about Authora.
          </p>
        </div>
        <div className="mt-12 space-y-2">
          {FAQ_ITEMS.map((item, i) => (
            <div
              key={i}
              className="rounded-lg border border-border/60 bg-card overflow-hidden"
            >
              <button
                type="button"
                className="w-full px-6 py-4 text-left font-medium text-foreground hover:bg-muted/50 transition-colors flex justify-between items-center"
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                aria-expanded={openIndex === i}
              >
                {item.q}
                <span className="text-muted-foreground">
                  {openIndex === i ? '−' : '+'}
                </span>
              </button>
              {openIndex === i && (
                <div className="px-6 pb-4 text-muted-foreground text-sm leading-relaxed">
                  {item.a}
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-8 text-center">
          <Link href="/faq" className="text-sm font-medium text-primary hover:underline">
            View all FAQs →
          </Link>
        </div>
      </div>
    </section>
  );
}
