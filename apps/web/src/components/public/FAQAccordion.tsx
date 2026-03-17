'use client';

import { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface FAQItem {
  q: string;
  a: string;
}

interface FAQAccordionProps {
  items: FAQItem[];
  className?: string;
}

export function FAQAccordion({ items, className }: FAQAccordionProps) {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <div className={cn('space-y-3', className)}>
      {items.map((item, i) => (
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
  );
}
