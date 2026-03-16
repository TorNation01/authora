'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { PlanComparison } from '@/components/billing/PlanComparison';

interface PlanPrice {
  monthly_cents: number | null;
  yearly_cents: number | null;
  lifetime_cents: number | null;
}

interface PlanFromApi {
  id: string;
  slug: string;
  name: string;
  limits: Record<string, unknown>;
  features: string[];
  price?: PlanPrice | null;
}

const FEATURE_LABELS: Record<string, string> = {
  planning: 'Guided planning',
  editor: 'Distraction-free editor',
  notes: 'Notes & research',
  accountability: 'Goals & accountability',
  gamification: 'Celebrations & streaks',
  ai: 'AI assistance',
  ghostwriter: 'Ghostwriter mode',
  export_pdf: 'Export to PDF',
  export_epub: 'Export to EPUB',
  publishing_prep: 'Publishing prep tools',
  finish_mode: 'Finish Mode',
  semantic_search: 'Semantic search / RAG',
  premium_model_routing: 'Premium model routing',
};

const DEFAULT_DESCRIPTIONS: Record<string, string> = {
  free: 'Get started. No credit card.',
  starter: 'For authors building their first books.',
  pro: 'For serious authors who want to finish.',
  studio: 'For professionals and power users.',
  founder_lifetime: 'One-time. Lifetime access. Support the project.',
};

function formatPrice(cents: number | null | undefined): string {
  if (cents == null) return '—';
  return `$${(cents / 100).toFixed(0)}`;
}

export function PricingContent() {
  const [plans, setPlans] = useState<PlanFromApi[]>([]);
  const [billingInterval, setBillingInterval] = useState<'monthly' | 'yearly'>('yearly');

  useEffect(() => {
    api<PlanFromApi[]>('/api/v1/billing/plans')
      .then(setPlans)
      .catch(() => setPlans([]));
  }, []);

  const paidPlans = plans.filter((p) => p.slug !== 'free');
  const freePlan = plans.find((p) => p.slug === 'free');
  const founderPlan = plans.find((p) => p.slug === 'founder_lifetime');
  const subscriptionPlans = paidPlans.filter((p) => p.slug !== 'founder_lifetime');

  if (plans.length === 0) {
    return (
      <div className="mt-16 grid gap-8 lg:grid-cols-2">
        <div className="card-sanctuary rounded-xl p-8">
          <h2 className="font-serif text-2xl font-semibold text-foreground">Free</h2>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold text-foreground">$0</span>
            <span className="text-muted-foreground">forever</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">Get started. No credit card.</p>
          <Button asChild variant="outline" className="mt-8 w-full">
            <Link href="/register">Start free</Link>
          </Button>
        </div>
        <div className="card-sanctuary rounded-xl p-8 ring-2 ring-primary shadow-lg">
          <span className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
            Most popular
          </span>
          <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">Pro</h2>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold text-foreground">$24</span>
            <span className="text-muted-foreground">/month</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">For serious authors.</p>
          <Button asChild className="mt-8 w-full">
            <Link href="/register">Get started</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="mt-8 flex justify-center">
        <div className="inline-flex rounded-lg border border-muted bg-muted/30 p-1">
          <button
            type="button"
            onClick={() => setBillingInterval('monthly')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              billingInterval === 'monthly' ? 'bg-background shadow' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Monthly
          </button>
          <button
            type="button"
            onClick={() => setBillingInterval('yearly')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              billingInterval === 'yearly' ? 'bg-background shadow' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Yearly
            <span className="ml-1.5 rounded bg-primary/20 px-1.5 py-0.5 text-xs text-primary">Save 25%</span>
          </button>
        </div>
      </div>

      <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
        {freePlan && (
          <div className="card-sanctuary rounded-xl p-8">
            <h2 className="font-serif text-2xl font-semibold text-foreground">{freePlan.name}</h2>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="text-3xl font-bold text-foreground">$0</span>
              <span className="text-muted-foreground">forever</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{DEFAULT_DESCRIPTIONS[freePlan.slug] ?? freePlan.name}</p>
            <ul className="mt-6 space-y-3">
              {(freePlan.features || []).slice(0, 6).map((f) => (
                <li key={f} className="flex items-start gap-3 text-sm">
                  <Check className="h-5 w-5 shrink-0 text-primary" />
                  {FEATURE_LABELS[f] ?? f}
                </li>
              ))}
            </ul>
            <Button asChild variant="outline" className="mt-8 w-full">
              <Link href="/register">Start free</Link>
            </Button>
          </div>
        )}

        {subscriptionPlans.map((plan) => {
          const featured = plan.slug === 'pro';
          const price = plan.price;
          const amount = billingInterval === 'yearly' ? price?.yearly_cents : price?.monthly_cents;
          const displayPrice = amount != null ? formatPrice(amount) : '—';
          const period = billingInterval === 'yearly' ? '/year' : '/month';
          const features = (plan.features || []).map((f) => FEATURE_LABELS[f] ?? f);
          return (
            <div
              key={plan.id}
              className={`card-sanctuary rounded-xl p-8 ${
                featured ? 'ring-2 ring-primary shadow-lg' : ''
              }`}
            >
              {featured && (
                <span className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                  Most popular
                </span>
              )}
              <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">{plan.name}</h2>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-3xl font-bold text-foreground">{displayPrice}</span>
                <span className="text-muted-foreground">{period}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground">
                {DEFAULT_DESCRIPTIONS[plan.slug] ?? plan.name}
              </p>
              <ul className="mt-6 space-y-3">
                {features.slice(0, 8).map((f) => (
                  <li key={f} className="flex items-start gap-3 text-sm">
                    <Check className="h-5 w-5 shrink-0 text-primary" />
                    {f}
                  </li>
                ))}
              </ul>
              <Button
                asChild
                variant={featured ? 'default' : 'outline'}
                className="mt-8 w-full"
              >
                <Link href="/register">Get started</Link>
              </Button>
            </div>
          );
        })}

        {founderPlan && (
          <div className="card-sanctuary rounded-xl p-8 border-2 border-amber-500/30 bg-amber-500/5">
            <span className="inline-block rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-700 dark:text-amber-400">
              Founder
            </span>
            <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">{founderPlan.name}</h2>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="text-3xl font-bold text-foreground">
                {formatPrice(founderPlan.price?.lifetime_cents)}
              </span>
              <span className="text-muted-foreground">one-time</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">
              {DEFAULT_DESCRIPTIONS[founderPlan.slug]}
            </p>
            <ul className="mt-6 space-y-3">
              {(founderPlan.features || []).slice(0, 6).map((f) => (
                <li key={f} className="flex items-start gap-3 text-sm">
                  <Check className="h-5 w-5 shrink-0 text-primary" />
                  {FEATURE_LABELS[f] ?? f}
                </li>
              ))}
            </ul>
            <Button asChild variant="outline" className="mt-8 w-full border-amber-500/50 hover:bg-amber-500/10">
              <Link href="/register">Get Founder</Link>
            </Button>
          </div>
        )}
      </div>

      <div className="mt-16">
        <h2 className="mb-8 text-center font-serif text-2xl font-semibold">Compare plans</h2>
        <PlanComparison />
      </div>
    </>
  );
}
