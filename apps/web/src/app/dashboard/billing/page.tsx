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
  clearBillingCache,
  type BillingStatus,
} from '@/lib/billing';
import { UsageDisplay } from '@/components/billing/UsageDisplay';
import { CreditCard, Calendar, Zap, ArrowUpRight, FileText, Receipt } from 'lucide-react';

export default function BillingPage() {
  const { toast } = useToast();
  const config = useConfig();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);

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
            {status.access_source === 'free' && 'Free plan'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
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
