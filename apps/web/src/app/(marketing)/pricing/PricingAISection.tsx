'use client';

import { Bot, Wand2, Lightbulb, MessageSquare, FileEdit, PenLine } from 'lucide-react';

const AI_POINTS = [
  { icon: Wand2, text: 'Rewrite and refine passages' },
  { icon: Lightbulb, text: 'Generate ideas when stuck' },
  { icon: MessageSquare, text: 'Improve clarity and flow' },
  { icon: FileEdit, text: 'Expand outlines into drafts' },
  { icon: Bot, text: 'Use ghostwriter tools when needed' },
  { icon: PenLine, text: 'Keep your voice at the center' },
];

export function PricingAISection() {
  return (
    <section
      className="py-20 border-t border-white/[0.06]"
      data-analytics="pricing-ai"
    >
      <div className="mx-auto max-w-3xl text-center">
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl">
          AI that supports your writing, not replaces your voice
        </h2>
        <p className="mt-6 text-muted-foreground leading-relaxed">
          Use Authora&apos;s AI tools when you need help finding the right wording, improving flow,
          getting unstuck, shaping your ideas, or strengthening the manuscript. Stay in control of
          your voice while getting support exactly where you need it.
        </p>
        <ul className="mt-10 flex flex-wrap justify-center gap-3">
          {AI_POINTS.map((item) => (
            <li
              key={item.text}
              className="flex items-center gap-2 rounded-full border border-white/[0.08] bg-card px-5 py-2.5 text-sm text-muted-foreground shadow-[var(--shadow-card-premium)]"
            >
              <item.icon className="h-4 w-4 text-primary" />
              {item.text}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
