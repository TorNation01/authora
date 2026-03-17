'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';

export function PricingHero() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section className="relative overflow-hidden border-b border-border/60 bg-gradient-to-b from-primary/5 via-transparent to-transparent">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.08),transparent)]" />
      <div className="relative mx-auto max-w-4xl px-4 py-16 text-center sm:px-6 sm:py-20 lg:px-8">
        <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl">
          Plans for every kind of writer
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
          Whether you are outlining your first idea, finishing your next manuscript, or building a
          full writing habit, Authora gives you the tools, structure, and support to keep moving.
        </p>
        <p className="mt-4 font-serif text-base font-medium text-foreground">
          Write with clarity. Stay accountable. Finish what you start.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          {feature_flags.standalone_auth && (
            <>
              <Button asChild size="lg" className="min-w-[180px]" data-analytics="cta-pricing-start-free">
                <Link href={`${getAppBaseUrl()}/register`}>Start Free</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-w-[180px]">
                <Link href="#compare-plans">Compare Plans</Link>
              </Button>
            </>
          )}
        </div>
        <p className="mt-4 text-sm text-muted-foreground">
          Upgrade anytime as your writing grows.
        </p>
      </div>
    </section>
  );
}
