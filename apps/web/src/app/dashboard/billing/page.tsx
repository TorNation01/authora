'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { useConfig } from '@/contexts/ConfigProvider';
import { useToast } from '@/hooks/use-toast';
import {
  getBillingStatus,
  createCustomerPortalSession,
  createCheckoutSession,
  createTemplatePackCheckout,
  clearBillingCache,
  type BillingStatus,
} from '@/lib/billing';
import { UsageDisplay } from '@/components/billing/UsageDisplay';
import { api } from '@/lib/api';
import { CreditCard, Calendar, Zap, ArrowUpRight, FileText, Receipt, BookOpen, Loader2 } from 'lucide-react';

type TemplatePack = {
  slug: string;
  name: string;
  description: string | null;
  price_cents: number;
  template_slugs: string[];
  purchased: boolean;
};

export default function BillingPage() {
  const { toast } = useToast();
  const config = useConfig();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [packs, setPacks] = useState<TemplatePack[]>([]);
  const [purchasingSlug, setPurchasingSlug] = useState<string | null>(null);
  // Plan intent carried through signup from /pricing (see register page). The
  // trial is already running; this is the one-click path to the tier they
  // actually asked for, instead of making them find pricing a second time.
  const [intent, setIntent] = useState<{
    slug: string;
    interval: string;
    name: string;
    cents: number | null;
  } | null>(null);
  const [activating, setActivating] = useState(false);

  useEffect(() => {
    const paramSlug = searchParams.get('plan');
    let slug = paramSlug;
    let interval = searchParams.get('interval') || 'monthly';
    if (!slug) {
      try {
        slug = window.localStorage.getItem('authora.intent.plan');
        interval = window.localStorage.getItem('authora.intent.interval') || interval;
      } catch {
        slug = null;
      }
    }
    if (!slug) return;
    let cancelled = false;
    api<Array<{ slug: string; name: string; price?: { monthly_cents?: number | null; yearly_cents?: number | null } }>>(
      '/api/v1/billing/plans'
    )
      .then((plans) => {
        if (cancelled) return;
        const plan = plans.find((p) => p.slug === slug);
        if (!plan) return;
        const cents =
          interval === 'yearly'
            ? plan.price?.yearly_cents ?? null
            : plan.price?.monthly_cents ?? null;
        setIntent({ slug, interval, name: plan.name, cents });
      })
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [searchParams]);

  const handleActivateIntent = async () => {
    if (!intent) return;
    setActivating(true);
    const result = await createCheckoutSession(intent.slug, intent.interval, {
      successUrl: `${window.location.origin}/dashboard/billing?success=1`,
      cancelUrl: `${window.location.origin}/dashboard/billing?canceled=1`,
    });
    if (result?.url) {
      window.location.href = result.url;
      return;
    }
    setActivating(false);
    toast({ title: 'Failed to start checkout', variant: 'destructive' });
  };

  useEffect(() => {
    const success = searchParams.get('success');
    const canceled = searchParams.get('canceled');
    if (success === '1') {
      clearBillingCache();
      toast({ title: 'Subscription updated successfully' });
    }
    if (canceled === '1') {
      clearBillingCache();
      toast({ title: 'Checkout canceled', variant: 'default' });
    }
  }, [searchParams, toast]);

  useEffect(() => {
    getBillingStatus()
      .then(setStatus)
      .finally(() => setLoading(false));
  }, [searchParams]);

  useEffect(() => {
    api<TemplatePack[]>('/api/v1/templates/packs')
      .then(setPacks)
      .catch(() => setPacks([]));
  }, []);

  const handlePurchasePack = async (packSlug: string) => {
    setPurchasingSlug(packSlug);
    try {
      const result = await createTemplatePackCheckout(packSlug, {
        successUrl: `${window.location.origin}/dashboard/billing?pack_purchased=1`,
        cancelUrl: window.location.href,
      });
      if (result?.url) {
        window.location.href = result.url;
      } else {
        toast({ title: 'Checkout not available', variant: 'destructive' });
      }
    } catch {
      toast({ title: 'Failed to start checkout', variant: 'destructive' });
    } finally {
      setPurchasingSlug(null);
    }
  };

  useEffect(() => {
    const purchased = searchParams.get('pack_purchased');
    if (purchased === '1') {
      clearBillingCache();
      toast({ title: 'Template pack purchased successfully' });
      api<TemplatePack[]>('/api/v1/templates/packs').then(setPacks).catch(() => {});
    }
  }, [searchParams, toast]);

  const handleManageBilling = async () => {
    const result = await createCustomerPortalSession(window.location.href);
    if (result?.url) {
      window.location.href = result.url;
    } else {
      toast({ title: 'Billing portal not available', variant: 'destructive' });
    }
  };

  if (!config.feature_flags.billing) {
    return (
      <div className="p-6 lg:p-8 max-w-xl">
        <PageHeader title="Billing" description="Plans and subscription" />
        <Card variant="soft">
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Billing is not enabled for this deployment. Contact your administrator.
            </p>
            <Button asChild variant="outline" className="mt-4">
              <Link href="/pricing">View pricing</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading || !status) {
    return (
      <div className="p-6 lg:p-8 max-w-xl">
        <PageHeader title="Billing" description="Plans and subscription" />
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  const sub = status.subscription;
  const trial = status.trial;
  const isLifetime =
    sub?.is_lifetime ?? status.plan.slug === 'founder_lifetime';
  const renewalDate = sub?.period_end ? new Date(sub.period_end) : null;
  const isCanceled = sub?.cancel_at_period_end ?? false;

  return (
    <div className="p-6 lg:p-8 max-w-2xl space-y-8">
      <PageHeader
        title="Billing, Plans, and Access"
        description="Manage your subscription and view usage"
      />

      {intent && !isLifetime && status.access_source !== 'stripe' && (
        <Card variant="sanctuary" data-analytics="intent-checkout">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              You picked {intent.name}
            </CardTitle>
            <CardDescription>
              {trial?.active
                ? `Your trial is running with ${trial.days_left === 1 ? '1 day' : `${trial.days_left} days`} left — activate ${intent.name} now and nothing changes except your limits.`
                : `Activate ${intent.name} to keep full access.`}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-semibold text-foreground">
                {intent.cents != null ? `$${(intent.cents / 100).toFixed(0)}` : '—'}
              </span>
              <span className="text-sm text-muted-foreground">
                /{intent.interval === 'yearly' ? 'year' : intent.interval === 'lifetime' ? 'once' : 'month'}
              </span>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleActivateIntent} disabled={activating}>
                {activating ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  `Activate ${intent.name}`
                )}
              </Button>
              <Button asChild variant="outline">
                <Link href="/dashboard">Keep writing on the trial</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
      <Card variant="sanctuary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Current plan
          </CardTitle>
          <CardDescription>
            {status.access_source === 'grant' && 'Complimentary Access'}
            {status.access_source === 'override' && 'Plan Override'}
            {status.access_source === 'stripe' && 'Stripe subscription'}
            {status.access_source === 'trial' && 'Free trial'}
            {status.access_source === 'free' && 'Free plan'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {trial?.active && (
            <div className="rounded-lg border border-primary/30 bg-primary/5 p-3">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {trial.days_left === 1 ? '1 day left' : `${trial.days_left} days left`} in your free trial
                  </p>
                  <p className="text-xs text-muted-foreground">
                    You have {status.plan.name} access until{' '}
                    {trial.ends_at ? new Date(trial.ends_at).toLocaleDateString() : 'your trial ends'}.
                    Pick a plan to keep it.
                  </p>
                </div>
                <Button asChild size="sm">
                  <Link href="/pricing">Choose a plan</Link>
                </Button>
              </div>
            </div>
          )}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-2xl font-semibold text-foreground">{status.plan.name}</p>
              {isLifetime && (
                <span className="inline-block mt-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  Lifetime Access
                </span>
              )}
              {isCanceled && !isLifetime && (
                <span className="inline-block mt-1 rounded-full bg-destructive/10 px-2 py-0.5 text-xs font-medium text-destructive">
                  Access ends at renewal
                </span>
              )}
            </div>
            {status.can_upgrade && (
              <Button asChild size="sm">
                <Link href="/pricing">
                  Upgrade
                  <ArrowUpRight className="ml-1 h-4 w-4" />
                </Link>
              </Button>
            )}
          </div>

          {renewalDate && !isLifetime && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>
                Renewal date: {renewalDate.toLocaleDateString()}
                {isCanceled && ' (Access ends)'}
              </span>
            </div>
          )}

          {status.subscription?.has_stripe_customer && (
            <div className="flex flex-wrap gap-2">
              <Button variant="outline" size="sm" onClick={handleManageBilling}>
                Manage billing
              </Button>
              <Button asChild variant="outline" size="sm">
                <Link href="/pricing">Change plan</Link>
              </Button>
            </div>
          )}

          {!status.subscription?.has_stripe_customer && status.can_upgrade && (
            <Button asChild size="sm">
              <Link href="/pricing">View Pricing</Link>
            </Button>
          )}
        </CardContent>
      </Card>

      {status.feature_billing_enabled && !status.billing_exempt && (
        <Card variant="soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Usage overview
            </CardTitle>
            <CardDescription>AI allowance and usage this period</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageDisplay />
          </CardContent>
        </Card>
      )}

      {status.subscription?.has_stripe_customer && (
        <Card variant="soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              Billing history & payment
            </CardTitle>
            <CardDescription>
              View invoices, update payment method, cancel or resume subscription
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" onClick={handleManageBilling}>
              Open billing portal
            </Button>
          </CardContent>
        </Card>
      )}

      {packs.length > 0 && (
        <Card variant="soft">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Template packs
            </CardTitle>
            <CardDescription>
              One-time purchases. Unlock premium templates forever.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {packs.map((pack) => (
              <div
                key={pack.slug}
                className="flex items-center justify-between rounded-lg border p-3"
              >
                <div>
                  <p className="font-medium">{pack.name}</p>
                  {pack.description && (
                    <p className="text-sm text-muted-foreground mt-0.5">{pack.description}</p>
                  )}
                  <p className="text-xs text-muted-foreground mt-1">
                    {pack.template_slugs.length} templates
                  </p>
                </div>
                <div className="shrink-0 ml-4">
                  {pack.purchased ? (
                    <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                      Owned
                    </span>
                  ) : (
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        ${(pack.price_cents / 100).toFixed(0)}
                      </span>
                      <Button
                        size="sm"
                        onClick={() => handlePurchasePack(pack.slug)}
                        disabled={purchasingSlug === pack.slug}
                      >
                        {purchasingSlug === pack.slug ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          'Purchase'
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <Button asChild variant="outline" size="sm" className="mt-2">
              <Link href="/dashboard/templates">Browse templates</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <Card variant="soft">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Plan comparison
          </CardTitle>
          <CardDescription>Compare plans and upgrade when you are ready</CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild variant="outline">
            <Link href="/pricing#compare-plans">Compare plans</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
