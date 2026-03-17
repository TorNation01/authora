'use client';

import { useState } from 'react';

const FAQ_ITEMS = [
  {
    q: 'Does Authora include a real editor?',
    a: 'Yes. Authora includes a full manuscript editor designed for book-length writing, with chapters, notes, and revision tools.',
  },
  {
    q: 'Can I work on more than one book?',
    a: 'Yes. Free allows 1 book; Starter allows 3; Pro and Studio allow unlimited or high limits. Founder Lifetime includes unlimited projects.',
  },
  {
    q: 'Is AI included?',
    a: 'Yes. All plans include some AI assistance. Free has limited AI; Starter and above have standard or better AI. Pro and Studio include ghostwriter tools.',
  },
  {
    q: 'Will Authora write the whole book for me?',
    a: 'No. You stay in control. Use AI as much or as little as you want—from light support to ghostwriter-style assistance. Your voice leads.',
  },
  {
    q: 'Can I upgrade later?',
    a: 'Yes. Upgrade anytime as your writing grows. Your plan is prorated when you upgrade.',
  },
  {
    q: 'Do you offer yearly billing?',
    a: 'Yes. Yearly billing saves you money compared to monthly. Choose monthly or yearly when you subscribe.',
  },
  {
    q: 'Is there a lifetime option?',
    a: 'Yes. Founder Lifetime is a special one-time plan for early supporters. It includes lifetime access to core Authora features.',
  },
  {
    q: 'Can Authora help with both fiction and non-fiction?',
    a: 'Yes. Authora supports fiction, non-fiction, memoir, workbooks, and more. Built for every kind of writer.',
  },
  {
    q: 'Is my writing private?',
    a: 'Yes. Your content is encrypted and private. We do not train on your content. See our Privacy Policy for details.',
  },
  {
    q: 'Can I export my work?',
    a: 'Yes. Export to DOCX, PDF, EPUB, and plain text. One click to share with beta readers, query agents, or publish.',
  },
];

export function PricingFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section className="py-20 border-t border-border/60" data-analytics="pricing-faq">
      <h2 className="font-serif text-2xl font-bold text-center text-foreground sm:text-3xl">
        Frequently asked questions
      </h2>
      <div className="mx-auto mt-12 max-w-2xl space-y-2">
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
    </section>
  );
}
