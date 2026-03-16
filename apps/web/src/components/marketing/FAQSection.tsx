'use client';

import { useState } from 'react';

const FAQ_ITEMS = [
  {
    q: 'Is Authora only for fiction writers?',
    a: 'No. Authora supports both fiction and non-fiction writers, including novels, memoirs, self-help books, business books, workbooks, journals, and more.',
  },
  {
    q: 'Does Authora include an editor?',
    a: 'Yes. Authora includes a real manuscript editor designed for actual book writing, not just idea generation.',
  },
  {
    q: 'Can Authora help me if I get stuck?',
    a: 'Yes. Authora includes AI-supported guidance, idea generation, rewriting help, and structure support to help you keep moving.',
  },
  {
    q: 'Can I use Authora for more than one book?',
    a: 'Yes. Depending on your plan, you can manage multiple active book projects.',
  },
  {
    q: 'Will Authora write the book for me?',
    a: 'It can help as much or as little as you want. You stay in control, and you can use the platform for planning, drafting, support, or stronger ghostwriter-style assistance.',
  },
  {
    q: 'Do I need to be a professional writer?',
    a: 'Not at all. Authora is built for first-time writers as well as experienced authors.',
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
          <a href="/faq" className="text-sm font-medium text-primary hover:underline">
            View all FAQs →
          </a>
        </div>
      </div>
    </section>
  );
}
