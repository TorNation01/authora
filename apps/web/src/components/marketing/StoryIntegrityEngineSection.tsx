'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import {
  Search,
  GitBranch,
  Users,
  Target,
  Clock,
  Sparkles,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';

const FEATURES = [
  { icon: GitBranch, label: 'Unresolved plot and idea detection' },
  { icon: Users, label: 'Weak or incomplete character arcs' },
  { icon: Target, label: 'Missing payoff' },
  { icon: Target, label: 'Structure and pacing insights' },
  { icon: Clock, label: 'Continuity checks' },
  { icon: Sparkles, label: 'Guided fix suggestions' },
];

export function StoryIntegrityEngineSection() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-border/60 bg-gradient-to-br from-card via-card to-primary/5"
      data-analytics="story-integrity-engine"
    >
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_100%_0%,hsl(var(--primary)/0.08),transparent)]" />
      <div className="relative p-8 sm:p-10 lg:p-12">
        <div className="flex flex-col gap-10 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1">
            <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/15 ring-1 ring-primary/20">
              <Search className="h-8 w-8 text-primary" />
            </div>
            <p className="text-sm font-medium uppercase tracking-wider text-primary/90">
              Story Integrity Engine™
            </p>
            <h2 className="mt-2 font-serif text-2xl font-bold text-foreground sm:text-3xl">
              Know what your story is missing.
            </h2>
            <p className="mt-4 max-w-xl text-muted-foreground leading-relaxed">
              Authora detects unresolved threads, weak arcs, missing payoff, and structural gaps — then
              helps you fix them with clarity.
            </p>
            <p className="mt-6 font-serif text-lg font-medium text-foreground">
              Find what is missing. Fix what matters. Finish stronger.
            </p>
            <ul className="mt-8 space-y-4">
              {FEATURES.map((item) => (
                <li key={item.label} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10">
                    <item.icon className="h-3 w-3 text-primary" />
                  </div>
                  <span className="text-sm text-muted-foreground">{item.label}</span>
                </li>
              ))}
            </ul>
            <div className="mt-8 rounded-lg border border-border/60 bg-muted/30 p-4">
              <p className="flex items-start gap-3 text-sm text-muted-foreground">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" />
                <span>
                  Instead of guessing what feels off, you can see what still needs support and where
                  to fix it.
                </span>
              </p>
            </div>
          </div>
          <div className="flex shrink-0 flex-col items-start gap-4 lg:min-w-[200px]">
            {feature_flags.standalone_auth && (
              <>
                <Button asChild size="lg" className="w-full sm:w-auto" data-analytics="cta-integrity-start">
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
