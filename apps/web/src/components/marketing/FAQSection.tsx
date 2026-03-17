'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ChevronDown } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';
import { cn } from '@/lib/utils';

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
    <section
      className="border-t border-white/[0.06] bg-muted/20 py-[var(--section-padding-y)]"
      data-analytics="faq"
    >
      <div className="mx-auto max-w-3xl px-[var(--section-padding-x)]">
        <div className="text-center">
          <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
            Frequently asked questions
          </h2>
          <p className="mt-4 text-muted-foreground">
            Everything you need to know about Authora.
          </p>
        </div>

        <div className="mt-12 space-y-3">
          {FAQ_ITEMS.map((item, i) => (
            <div
              key={i}
              className="rounded-xl border border-white/[0.08] bg-white/[0.02] overflow-hidden transition-colors hover:border-white/[0.12]"
            >
              <button
                type="button"
                className="w-full px-6 py-5 text-left font-medium text-foreground flex justify-between items-center gap-4 transition-colors hover:bg-white/[0.02]"
                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                aria-expanded={openIndex === i}
                aria-controls={`faq-answer-${i}`}
                id={`faq-question-${i}`}
              >
                <span>{item.q}</span>
                <ChevronDown
                  className={cn(
                    'h-5 w-5 shrink-0 text-muted-foreground transition-transform duration-200',
                    openIndex === i && 'rotate-180'
                  )}
                />
              </button>
              <div
                id={`faq-answer-${i}`}
                role="region"
                aria-labelledby={`faq-question-${i}`}
                className={cn(
                  'grid transition-all duration-200 ease-out',
                  openIndex === i ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
                )}
              >
                <div className="overflow-hidden">
                  <div className="px-6 pb-5 text-muted-foreground text-sm leading-relaxed border-t border-white/[0.06] pt-4">
                    {item.a}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center gap-6">
          <CTAPair
            primary="start-free"
            secondary="view-pricing"
            microcopy={CTA_MICROCOPY.faqClose}
            analyticsPrefix="faq-"
          />
          <Link
            href="/faq"
            className="text-sm font-medium text-primary hover:underline inline-flex items-center gap-1"
          >
            View all FAQs
            <span aria-hidden>→</span>
          </Link>
        </div>
      </div>
    </section>
  );
}
