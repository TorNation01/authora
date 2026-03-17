'use client';

import { FAQAccordion, type FAQItem } from '@/components/public/FAQAccordion';

interface FeaturePageFAQProps {
  title?: string;
  items: FAQItem[];
}

export function FeaturePageFAQ({
  title = 'Frequently asked questions',
  items,
}: FeaturePageFAQProps) {
  return (
    <section className="border-t border-white/[0.06] py-[var(--section-padding-y)]">
      <div className="mx-auto max-w-3xl px-[var(--section-padding-x)]">
        <h2 className="font-serif text-2xl font-bold text-center text-foreground sm:text-3xl">
          {title}
        </h2>
        <div className="mt-12">
          <FAQAccordion items={items} />
        </div>
      </div>
    </section>
  );
}
