'use client';

import { useState } from 'react';

const FAQ_ITEMS = [
  {
    q: 'What is AUTHORA?',
    a: 'AUTHORA is a guided writing platform that helps you finish your book. It combines planning tools, a distraction-free editor, AI assistance when you need it, and accountability features—all in one place. Whether you write fiction or non-fiction, AUTHORA adapts to your genre and workflow.',
  },
  {
    q: 'How does the AI work?',
    a: 'AUTHORA\'s AI is built to assist, not replace. You can use it for suggestions, rewrites, expansion, or drafting. You control when and how much AI is involved. Your voice stays in the driver\'s seat.',
  },
  {
    q: 'Can I use it for both fiction and non-fiction?',
    a: 'Yes. We have templates and workflows for fiction (romance, thriller, fantasy, mystery) and non-fiction (memoir, business, self-help, educational, thought leadership). Each template includes setup questions, outline suggestions, and milestone maps.',
  },
  {
    q: 'How does accountability work?',
    a: 'Set daily or weekly word goals. Choose your encouragement style—gentle, balanced, or structured. We send reminders and recovery nudges when you\'ve been away. The goal is support, not guilt.',
  },
  {
    q: 'What formats can I export?',
    a: 'DOCX, PDF, EPUB, and plain text. Export your full manuscript, outline, or individual chapters. Ready for querying agents or self-publishing.',
  },
  {
    q: 'Is there a free tier?',
    a: 'Yes. You can start writing for free. No credit card required. Upgrade when you need more features or support.',
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
            Everything you need to know about AUTHORA.
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
