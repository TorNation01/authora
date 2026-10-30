'use client';

import React, { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { createCheckoutSession } from '@/lib/billing';
import { hasToken } from '@/lib/auth';
import { useToast } from '@/hooks/use-toast';
import { Check, Loader2, Sparkles, Crown, Zap } from 'lucide-react';
import { DEFAULT_PLANS, type PlanSlug } from '@/content/pricing-copy';

function formatPrice(cents: number | null): string {
  if (cents == null) return '—';
  return `$${(cents / 100).toFixed(0)}`;
}

interface PricingPlanCardsProps {
  billingInterval: 'monthly' | 'yearly';
  onBillingIntervalChange?: (v: 'monthly' | 'yearly') => void;
}

export function PricingPlanCards({ billingInterval }: PricingPlanCardsProps) {
  const config = useConfig();
  const { toast } = useToast();
  const { feature_flags } = config;
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null);
  const [checkoutPlan, setCheckoutPlan] = useState<string | null>(null);
  // Live prices from the billing API. The copy file is only a fallback: the
  // page must never advertise a number the checkout will not charge.
  const [livePrices, setLivePrices] = useState<
    Record<string, { monthly: number | null; yearly: number | null; lifetime: number | null }>
  >({});
  // Lifetime is a limited-time offer: the billing API tells us whether the
  // window is open. Absent/false means the card is not rendered at all.
  const [lifetimeOffer, setLifetimeOffer] = useState<{
    available: boolean;
    ends_at: string | null;
  } | null>(null);

  useEffect(() => {
    setIsLoggedIn(hasToken());
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/v1/billing/plans')
      .then((r) => (r.ok ? r.json() : []))
      .then((plans: Array<{ slug: string; price?: { monthly_cents?: number | null; yearly_cents?: number | null; lifetime_cents?: number | null } | null; lifetime_offer?: { available?: boolean; ends_at?: string | null } | null }>) => {
        if (cancelled || !Array.isArray(plans)) return;
        const next: typeof livePrices = {};
        for (const p of plans) {
          if (!p?.slug) continue;
          next[p.slug] = {
            monthly: p.price?.monthly_cents ?? null,
            yearly: p.price?.yearly_cents ?? null,
            lifetime: p.price?.lifetime_cents ?? null,
          };
          if (p.slug === 'founder_lifetime') {
            setLifetimeOffer({
              available: Boolean(p.lifetime_offer?.available),
              ends_at: p.lifetime_offer?.ends_at ?? null,
            });
          }
        }
        setLivePrices(next);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
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

  const renderPlanCard = (
    slug: PlanSlug,
    plan: (typeof DEFAULT_PLANS)[PlanSlug],
    isFree: boolean,
    isPro: boolean,
    isStudio: boolean,
    isFounder: boolean
  ) => {
    const live = livePrices[slug];
    const monthlyCents = live?.monthly ?? plan.monthly_cents ?? 0;
    const yearlyCents = live?.yearly ?? plan.yearly_cents ?? 0;
    const displayPrice = isFree
      ? '$0'
      : billingInterval === 'yearly'
        ? formatPrice(yearlyCents)
        : formatPrice(monthlyCents);
    const period = isFree ? 'forever' : billingInterval === 'yearly' ? '/year' : '/month';
    const annualSavings =
      !isFree && monthlyCents > 0 && yearlyCents > 0
        ? Math.round((1 - yearlyCents / 12 / monthlyCents) * 100)
        : 0;

    const cardClasses = [
      'relative rounded-2xl border p-6 lg:p-8 transition-all duration-200',
      isPro &&
        'border-primary/50 bg-primary/[0.06] ring-2 ring-primary/30 shadow-[var(--shadow-card-premium)] scale-[1.02]',
      isStudio && !isPro && 'border-primary/30 bg-card',
      !isPro && !isStudio && 'border-white/[0.08] bg-card',
    ]
      .filter(Boolean)
      .join(' ');

    return (
      <div key={slug} className={cardClasses}>
        {isPro && (
          <div className="absolute -top-3 left-1/2 -translate-x-1/2">
            <span className="inline-flex items-center gap-1 rounded-full bg-primary px-4 py-1 text-xs font-semibold text-primary-foreground shadow-md">
              <Sparkles className="h-3.5 w-3.5" />
              Most Popular
            </span>
          </div>
        )}
        {isStudio && !isPro && (
          <div className="absolute -top-3 left-1/2 -translate-x-1/2">
            <span className="inline-flex items-center gap-1 rounded-full border border-primary/40 bg-card px-4 py-1 text-xs font-semibold text-primary">
              <Crown className="h-3.5 w-3.5" />
              Premium
            </span>
          </div>
        )}
        {plan.badge && !isPro && !isStudio && (
          <span className="inline-block rounded-full bg-amber-500/20 px-3 py-1 text-xs font-medium text-amber-600 dark:text-amber-400">
            {plan.badge}
          </span>
        )}

        <h2 className="mt-4 font-serif text-xl font-semibold text-foreground">{plan.name}</h2>
        <div className="mt-3 flex items-baseline gap-1">
          <span className="text-3xl font-bold tracking-tight text-foreground">{displayPrice}</span>
          <span className="text-muted-foreground">{period}</span>
        </div>
        {!isFree && billingInterval === 'yearly' && annualSavings > 0 && (
          <p className="mt-1 text-xs font-medium text-success">
            Save {annualSavings}% vs monthly
          </p>
        )}
        {!isFree && billingInterval === 'yearly' && (
          <p className="mt-0.5 text-xs text-muted-foreground">
            {formatPrice(monthlyCents)}/mo billed annually
          </p>
        )}
        <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{plan.description}</p>
        <ul className="mt-6 space-y-3">
          {plan.features.map((f) => (
            <li key={f} className="flex items-start gap-3 text-sm">
              <Check className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
              <span className="text-muted-foreground">{f}</span>
            </li>
          ))}
        </ul>
        {feature_flags.standalone_auth && (
          isLoggedIn && !isFree ? (
            <Button
              variant={isPro ? 'default' : 'outline'}
              className="mt-8 w-full h-11 font-medium"
              disabled={checkoutPlan === slug}
              onClick={() => handleCheckout(slug, isFounder ? 'lifetime' : billingInterval)}
            >
              {checkoutPlan === slug ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                plan.cta
              )}
            </Button>
          ) : (
            <Button
              asChild
              variant={isPro ? 'default' : 'outline'}
              className="mt-8 w-full h-11 font-medium"
            >
              <Link href="/register">{plan.cta}</Link>
            </Button>
          )
        )}
      </div>
    );
  };

  return (
    <section className="py-16" data-analytics="pricing-plans">
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {subscriptionPlans.map((slug) => {
          const plan = DEFAULT_PLANS[slug];
          return renderPlanCard(
            slug,
            plan,
            slug === 'free',
            slug === 'pro',
            slug === 'studio',
            false
          );
        })}
      </div>

      {/* Lifetime Access — limited-time offer, only rendered while the window is open */}
      {lifetimeOffer?.available && (
      <div className="mt-6 overflow-hidden rounded-2xl border border-amber-500/30 bg-gradient-to-r from-amber-500/[0.10] via-amber-500/[0.05] to-transparent p-6 lg:p-8">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="max-w-2xl">
            <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-500/20 px-3 py-1 text-xs font-semibold text-amber-600 dark:text-amber-400">
              <Crown className="h-3.5 w-3.5" />
              Limited-time offer
            </span>
            <h2 className="mt-3 font-serif text-2xl font-semibold text-foreground">
              {DEFAULT_PLANS.founder_lifetime.name} — pay once, own it forever
            </h2>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
              {DEFAULT_PLANS.founder_lifetime.description}
            </p>
            <ul className="mt-4 grid gap-2 sm:grid-cols-2">
              {DEFAULT_PLANS.founder_lifetime.features.slice(0, 6).map((f) => (
                <li key={f} className="flex items-start gap-2 text-sm">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
                  <span className="text-muted-foreground">{f}</span>
                </li>
              ))}
            </ul>
          </div>
          <div className="shrink-0 text-center lg:text-right">
            <div className="flex items-baseline justify-center gap-1 lg:justify-end">
              <span className="text-4xl font-bold tracking-tight text-foreground">
                {formatPrice(
                  livePrices.founder_lifetime?.lifetime ??
                    DEFAULT_PLANS.founder_lifetime.lifetime_cents ??
                    49900
                )}
              </span>
              <span className="text-muted-foreground">once</span>
            </div>
            <p className="mt-1 text-xs text-muted-foreground">No subscription. No renewals. Ever.</p>
            {lifetimeOffer?.ends_at && (
              <p className="mt-1 text-xs font-medium text-amber-600 dark:text-amber-400">
                Offer ends{' '}
                {new Date(lifetimeOffer.ends_at).toLocaleDateString('en-AU', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                })}
              </p>
            )}
            {feature_flags.standalone_auth && isLoggedIn ? (
              <Button
                className="mt-4 h-11 w-full min-w-[220px] bg-amber-500 font-medium text-black hover:bg-amber-400"
                disabled={checkoutPlan === 'founder_lifetime'}
                onClick={() => handleCheckout('founder_lifetime', 'lifetime')}
              >
                {checkoutPlan === 'founder_lifetime' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  DEFAULT_PLANS.founder_lifetime.cta
                )}
              </Button>
            ) : (
              <Button
                asChild
                className="mt-4 h-11 w-full min-w-[220px] bg-amber-500 font-medium text-black hover:bg-amber-400"
              >
                <Link href="/register">
                  {DEFAULT_PLANS.founder_lifetime.cta}
                </Link>
              </Button>
            )}
          </div>
        </div>
      </div>
      )}
    </section>
  );
}
