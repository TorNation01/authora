'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { Brain, ArrowRight } from 'lucide-react';

export function EnginesCombinedSection() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-border/60 bg-gradient-to-b from-primary/10 via-transparent to-transparent"
      data-analytics="engines-combined"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />
      <div className="relative mx-auto max-w-4xl px-8 py-16 text-center sm:px-12 sm:py-20">
        <div className="mx-auto mb-8 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/15 ring-1 ring-primary/20">
          <Brain className="h-7 w-7 text-primary" />
        </div>
        <h2 className="font-serif text-2xl font-bold text-foreground sm:text-3xl lg:text-4xl">
          Not just writing tools — writing intelligence.
        </h2>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground leading-relaxed">
          Most tools give you a blank page. Authora gives you a system that helps you write,
          strengthen, and finish the manuscript properly.
        </p>
        <p className="mt-8 font-serif text-xl font-semibold text-foreground">
          Write better. Revise faster. Finish stronger.
        </p>
        {feature_flags.standalone_auth && (
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button asChild size="lg" data-analytics="cta-engines-combined">
              <Link href={`${getAppBaseUrl()}/register`}>
                Start Writing Free
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/pricing">View Pricing</Link>
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}
