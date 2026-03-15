'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { PlanComparison } from '@/components/billing/PlanComparison';

interface PlanFromApi {
  id: string;
  slug: string;
  name: string;
  limits: Record<string, unknown>;
  features: string[];
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
};

const PRICE_DISPLAY: Record<string, { price: string; period: string }> = {
  free: { price: '$0', period: 'forever' },
  pro: { price: 'TBD', period: '/month' },
  premium: { price: 'TBD', period: '/month' },
};

const DEFAULT_DESCRIPTIONS: Record<string, string> = {
  free: 'Get started. No credit card.',
  pro: 'For authors who want more.',
  premium: 'For serious authors who want to finish.',
};

export function PricingContent() {
  const [plans, setPlans] = useState<PlanFromApi[]>([]);

  useEffect(() => {
    api<PlanFromApi[]>('/api/v1/billing/plans')
      .then(setPlans)
      .catch(() => setPlans([]));
  }, []);

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
          <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">Premium</h2>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold text-foreground">TBD</span>
            <span className="text-muted-foreground">/month</span>
          </div>
          <p className="mt-2 text-sm text-muted-foreground">For serious authors.</p>
          <Button asChild className="mt-8 w-full">
            <Link href="/contact">Contact for early access</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        {plans.map((plan) => {
          const featured = plan.slug === 'premium';
          const display = PRICE_DISPLAY[plan.slug] ?? { price: 'TBD', period: '/month' };
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
              <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">
                {plan.name}
              </h2>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-3xl font-bold text-foreground">{display.price}</span>
                <span className="text-muted-foreground">{display.period}</span>
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
                <Link href={plan.slug === 'free' ? '/register' : '/contact'}>
                  {plan.slug === 'free' ? 'Start free' : 'Contact for early access'}
                </Link>
              </Button>
            </div>
          );
        })}
      </div>
      <div className="mt-16">
        <h2 className="font-serif text-2xl font-semibold text-center mb-8">
          Compare plans
        </h2>
        <PlanComparison />
      </div>
      <p className="mt-12 text-center text-sm text-muted-foreground">
        Premium pricing coming soon. Contact us for early access.
      </p>
    </>
  );
}
