'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { createCheckoutSession } from '@/lib/billing';
import { hasToken } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Check, Loader2 } from 'lucide-react';
import { DEFAULT_PLANS, type PlanSlug } from '@/content/pricing-copy';

function formatPrice(cents: number | null): string {
  if (cents == null) return '—';
  return `$${(cents / 100).toFixed(0)}`;
}

export function PricingPlanCards() {
  const config = useConfig();
  const { toast } = useToast();
  const { feature_flags } = config;
  const [billingInterval, setBillingInterval] = React.useState<'monthly' | 'yearly'>('yearly');
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const [checkoutPlan, setCheckoutPlan] = useState<string | null>(null);

  useEffect(() => {
    setIsLoggedIn(hasToken());
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    if (params.get('canceled') === '1') {
      toast({ title: 'Checkout canceled', variant: 'default' });
      window.history.replaceState({}, '', window.location.pathname);
    }
  }, [toast]);

  const handleCheckout = useCallback(
    async (planSlug: PlanSlug, interval: 'monthly' | 'yearly' | 'lifetime') => {
      if (!isLoggedIn) return;
      const base = typeof window !== 'undefined' ? window.location.origin : '';
      const appBase = getAppBaseUrl() || base;
      setCheckoutPlan(planSlug);
      try {
        const result = await createCheckoutSession(planSlug, interval, {
          successUrl: `${appBase}/dashboard/billing?success=1`,
          cancelUrl: `${base}/pricing?canceled=1`,
        });
        if (result?.url) {
          window.location.href = result.url;
        } else {
          toast({ title: 'Checkout unavailable', variant: 'destructive' });
        }
      } catch {
        toast({ title: 'Checkout failed', variant: 'destructive' });
      } finally {
        setCheckoutPlan(null);
      }
    },
    [isLoggedIn, toast]
  );

  const subscriptionPlans: PlanSlug[] = ['free', 'starter', 'pro', 'studio'];
  const founderPlan: PlanSlug = 'founder_lifetime';

  return (
    <section className="py-16" data-analytics="pricing-plans">
      <div className="flex justify-center">
        <div className="inline-flex rounded-lg border border-border/60 bg-muted/30 p-1">
          <button
            type="button"
            onClick={() => setBillingInterval('monthly')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              billingInterval === 'monthly'
                ? 'bg-background shadow text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Monthly
          </button>
          <button
            type="button"
            onClick={() => setBillingInterval('yearly')}
            className={`rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              billingInterval === 'yearly'
                ? 'bg-background shadow text-foreground'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Yearly
            <span className="ml-1.5 rounded bg-primary/20 px-1.5 py-0.5 text-xs text-primary">
              Save with yearly billing
            </span>
          </button>
        </div>
      </div>

      <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-5">
        {subscriptionPlans.map((slug) => {
          const plan = DEFAULT_PLANS[slug];
          const isFree = slug === 'free';
          const isPro = slug === 'pro';
          const isStudio = slug === 'studio';
          const monthlyCents = plan.monthly_cents ?? 0;
          const yearlyCents = plan.yearly_cents ?? 0;
          const displayPrice = isFree
            ? '$0'
            : billingInterval === 'yearly'
              ? formatPrice(yearlyCents)
              : formatPrice(monthlyCents);
          const period = isFree ? 'forever' : billingInterval === 'yearly' ? '/year' : '/month';

          return (
            <div
              key={slug}
              className={`relative rounded-2xl border p-6 lg:p-8 ${
                isPro
                  ? 'border-primary/50 bg-primary/5 ring-2 ring-primary/30 shadow-lg'
                  : isStudio
                    ? 'border-primary/30 bg-card'
                    : 'border-border/60 bg-card'
              }`}
            >
              {plan.badge && (
                <span
                  className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                    isPro
                      ? 'bg-primary/20 text-primary'
                      : isStudio
                        ? 'bg-primary/10 text-primary'
                        : 'bg-amber-500/20 text-amber-600 dark:text-amber-400'
                  }`}
                >
                  {plan.badge}
                </span>
              )}
              <h2 className="mt-4 font-serif text-xl font-semibold text-foreground">{plan.name}</h2>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="text-3xl font-bold text-foreground">{displayPrice}</span>
                <span className="text-muted-foreground">{period}</span>
              </div>
              {!isFree && billingInterval === 'yearly' && (
                <p className="mt-1 text-xs text-muted-foreground">
                  {formatPrice(monthlyCents)}/mo billed annually
                </p>
              )}
              <p className="mt-3 text-sm text-muted-foreground">{plan.description}</p>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-3 text-sm">
                    <Check className="h-5 w-5 shrink-0 text-primary" />
                    <span className="text-muted-foreground">{f}</span>
                  </li>
                ))}
              </ul>
              {feature_flags.standalone_auth && (
                isLoggedIn && !isFree ? (
                  <Button
                    variant={isPro ? 'default' : 'outline'}
                    className="mt-8 w-full"
                    disabled={checkoutPlan === slug}
                    onClick={() => handleCheckout(slug, billingInterval)}
                  >
                    {checkoutPlan === slug ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      plan.cta
                    )}
                  </Button>
                ) : (
                  <Button asChild variant={isPro ? 'default' : 'outline'} className="mt-8 w-full">
                    <Link href={`${getAppBaseUrl() || '/'}/register`}>{plan.cta}</Link>
                  </Button>
                )
              )}
            </div>
          );
        })}

        {/* Founder Lifetime */}
        <div className="relative rounded-2xl border-2 border-amber-500/30 bg-amber-500/5 p-6 lg:p-8">
          <span className="inline-block rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-600 dark:text-amber-400">
            {DEFAULT_PLANS[founderPlan].badge}
          </span>
          <h2 className="mt-4 font-serif text-xl font-semibold text-foreground">
            {DEFAULT_PLANS[founderPlan].name}
          </h2>
          <div className="mt-2 flex items-baseline gap-1">
            <span className="text-3xl font-bold text-foreground">
              {formatPrice(DEFAULT_PLANS[founderPlan].lifetime_cents)}
            </span>
            <span className="text-muted-foreground">once</span>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">
            {DEFAULT_PLANS[founderPlan].description}
          </p>
          <ul className="mt-6 space-y-3">
            {DEFAULT_PLANS[founderPlan].features.map((f) => (
              <li key={f} className="flex items-start gap-3 text-sm">
                <Check className="h-5 w-5 shrink-0 text-primary" />
                <span className="text-muted-foreground">{f}</span>
              </li>
            ))}
          </ul>
          {feature_flags.standalone_auth &&
            (isLoggedIn ? (
              <Button
                variant="outline"
                className="mt-8 w-full border-amber-500/50 hover:bg-amber-500/10"
                disabled={checkoutPlan === founderPlan}
                onClick={() => handleCheckout(founderPlan, 'lifetime')}
              >
                {checkoutPlan === founderPlan ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  DEFAULT_PLANS[founderPlan].cta
                )}
              </Button>
            ) : (
              <Button
                asChild
                variant="outline"
                className="mt-8 w-full border-amber-500/50 hover:bg-amber-500/10"
              >
                <Link href={`${getAppBaseUrl() || '/'}/register`}>{DEFAULT_PLANS[founderPlan].cta}</Link>
              </Button>
            ))}
        </div>
      </div>
    </section>
  );
}
