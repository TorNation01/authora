'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import {
  Scissors,
  Copy,
  Gauge,
  MinusSquare,
  BarChart3,
  ArrowRight,
  CheckCircle2,
  Repeat,
} from 'lucide-react';

const FEATURES = [
  { icon: Copy, label: 'Filler and clutter detection' },
  { icon: Repeat, label: 'Repeated beat / repeated argument detection' },
  { icon: Gauge, label: 'Chapter drag analysis' },
  { icon: MinusSquare, label: 'Thin-support detection' },
  { icon: Scissors, label: 'Trim vs strengthen guidance' },
  { icon: BarChart3, label: 'Chapter density scoring' },
];

export function StoryDensityEngineSection() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-border/60 bg-gradient-to-br from-card via-card to-success/5"
      data-analytics="story-density-engine"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_0%_0%,hsl(var(--success)/0.08),transparent)]" />
      <div className="relative p-8 sm:p-10 lg:p-12">
        <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-success/15 ring-1 ring-success/20">
              <Scissors className="h-8 w-8 text-success" />
            </div>
            <p className="text-sm font-medium uppercase tracking-wider text-success/90">
              Story Density Engine™
            </p>
            <h2 className="mt-2 font-serif text-2xl font-bold text-foreground sm:text-3xl">
              Cut the filler. Strengthen what matters.
            </h2>
            <p className="mt-4 max-w-xl text-muted-foreground leading-relaxed">
              Authora detects repetition, drag, filler, and weak sections — and shows you exactly
              what to trim, compress, or strengthen.
            </p>
            <p className="mt-6 font-serif text-lg font-medium text-foreground">
              Know what to cut. Know what to build. Write tighter, stronger books.
            </p>
            <ul className="mt-8 space-y-4">
              {FEATURES.map((item) => (
                <li key={item.label} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-success/10">
                    <item.icon className="h-3 w-3 text-success" />
                  </div>
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8 rounded-lg border border-border/60 bg-muted/30 p-4">
              <p className="flex items-start gap-3 text-sm text-muted-foreground">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-success" />
                <span>
                  Instead of over-editing blindly, you can see where the manuscript is bloated, where
                  it is too thin, and what to do next.
                </span>
              </p>
            </div>
          </div>
          <div className="flex shrink-0 flex-col items-start gap-4 lg:min-w-[200px]">
            {feature_flags.standalone_auth && (
              <>
                <Button asChild size="lg" className="w-full sm:w-auto" data-analytics="cta-density-start">
                  <Link href={`${getAppBaseUrl()}/register`}>
                    Start Writing Free
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="w-full sm:w-auto">
                  <Link href="/pricing">View Pricing</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
