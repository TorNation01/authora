'use client';

import { Brain, Scissors, Search } from 'lucide-react';

const INTELLIGENCE_POINTS = [
  {
    icon: Brain,
    title: 'Story Integrity Engine',
    text: 'Find what your story is missing—gaps, inconsistencies, and opportunities to deepen the narrative.',
  },
  {
    icon: Scissors,
    title: 'Story Density Engine',
    text: 'Cut filler, strengthen what matters. Identify weak passages and tighten your prose.',
  },
  {
    icon: Search,
    title: 'Smart search',
    text: 'Find anything across your manuscript, notes, and research vault in seconds.',
  },
];

export function PricingIntelligenceSection() {
  return (
    <section
      className="py-20 border-t border-white/[0.06]"
      data-analytics="pricing-intelligence"
    >
      <div className="mx-auto max-w-4xl">
        <h2 className="font-serif text-2xl font-bold text-center text-foreground sm:text-3xl">
          Writing intelligence that helps you level up
        </h2>
        <p className="mt-6 text-center text-muted-foreground max-w-2xl mx-auto">
          Pro and Studio include manuscript intelligence tools that go beyond spell-check—they help
          you see your story clearly and make it stronger.
        </p>
        <div className="mt-12 grid gap-6 sm:grid-cols-3">
          {INTELLIGENCE_POINTS.map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-white/[0.08] bg-card p-6 shadow-[var(--shadow-card-premium)]"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <item.icon className="h-6 w-6 text-primary" />
              </div>
              <h3 className="mt-4 font-semibold text-foreground">{item.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{item.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
