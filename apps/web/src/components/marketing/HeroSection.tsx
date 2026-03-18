'use client';

import { Check } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';
import { ProductPreview } from '@/components/marketing/ProductPreview';

const BULLETS = [
  'Know what to write next',
  'Fix what\'s not working',
  'Cut what doesn\'t matter',
  'Strengthen what does',
  'Finish your manuscript',
];

export function HeroSection() {
  return (
    <section
      className="relative min-h-[85vh] min-h-[85dvh] overflow-hidden flex items-center"
      data-analytics="hero"
    >
      {/* Background: black base + subtle gradient + soft gold glow */}
      <div className="absolute inset-0 bg-[hsl(var(--background))]" />
      <div className="absolute inset-0 bg-gradient-to-b from-primary/[0.06] via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-10%,hsl(var(--primary)/0.12),transparent_60%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_80%_80%,hsl(var(--primary)/0.04),transparent)]" />

      <div className="relative mx-auto w-full max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          {/* Headline - strong hierarchy */}
          <h1
            className="font-serif font-bold tracking-tight text-foreground opacity-0 animate-fade-up"
            style={{ fontSize: 'var(--text-hero)', lineHeight: 1.1 }}
          >
            Finally finish the book
            <br />
            <span className="text-primary">you&apos;ve been trying to write.</span>
          </h1>

          <p
            className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground font-serif leading-relaxed opacity-0 animate-fade-up animation-delay-100"
            style={{ animationFillMode: 'forwards' }}
          >
            Authora helps you start, structure, write, improve, and finish your book — with AI
            guidance, smart editing tools, and built-in momentum that keeps you moving.
          </p>

          {/* Value stack - concise bullets */}
          <ul
            className="mt-8 flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm font-medium text-muted-foreground opacity-0 animate-fade-up animation-delay-200"
            style={{ animationFillMode: 'forwards' }}
          >
            {BULLETS.map((b) => (
              <li key={b} className="flex items-center gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/20">
                  <Check className="h-3 w-3 text-primary" />
                </span>
                {b}
              </li>
            ))}
          </ul>

          {/* CTAs */}
          <div
            className="mt-10 opacity-0 animate-fade-up animation-delay-300"
            style={{ animationFillMode: 'forwards' }}
          >
            <CTAPair
              primary="start-writing-free"
              secondary="see-how-it-works"
              microcopy={CTA_MICROCOPY.hero}
              analyticsPrefix="hero-"
            />
          </div>

          {/* Live dynamic product preview - cycles through Writing studio, AI assist, Notes, Journey, Accountability, Export */}
          <div
            className="mt-16 flex justify-center opacity-0 animate-fade-up animation-delay-500"
            style={{ animationFillMode: 'forwards' }}
          >
            <ProductPreview />
          </div>
        </div>
      </div>
    </section>
  );
}
