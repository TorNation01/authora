'use client';

import React from 'react';
import Link from 'next/link';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { CONVERSION_COPY, type UpgradeTrigger } from '@/content/conversion-copy';
import { DEFAULT_PLANS } from '@/content/pricing-copy';
import { createCheckoutSession } from '@/lib/billing';
import { getAppBaseUrl } from '@/lib/config';
import { useToast } from '@/hooks/use-toast';
import { Check, Loader2, Sparkles } from 'lucide-react';

interface UpgradeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  trigger: UpgradeTrigger;
  featureLabel?: string;
}

function formatPrice(cents: number | null): string {
  if (cents == null) return '—';
  return `$${(cents / 100).toFixed(0)}`;
}

export function UpgradeModal({
  open,
  onOpenChange,
  trigger,
  featureLabel,
}: UpgradeModalProps) {
  const { toast } = useToast();
  const [checkoutPlan, setCheckoutPlan] = React.useState<string | null>(null);

  const copy = CONVERSION_COPY[trigger];
  const proPlan = DEFAULT_PLANS.pro;

  const handleUpgrade = async (planSlug: string, interval: 'monthly' | 'yearly') => {
    const base = typeof window !== 'undefined' ? window.location.origin : '';
    const appBase = getAppBaseUrl() || base;
    setCheckoutPlan(planSlug);
    try {
      const result = await createCheckoutSession(planSlug, interval, {
        successUrl: `${appBase}/dashboard/billing?success=1`,
        cancelUrl: `${base}/dashboard?canceled=1`,
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
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            {featureLabel ? `${featureLabel} — ${copy.title}` : copy.title}
          </DialogTitle>
          <DialogDescription>{copy.description}</DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-foreground">{copy.benefit}</p>

          <div className="rounded-lg border border-border/60 bg-muted/30 p-4">
            <p className="text-sm font-medium text-foreground">Pro — {proPlan.description}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-2xl font-bold text-foreground">
                {formatPrice(proPlan.monthly_cents)}/mo
              </span>
              <span className="text-sm text-muted-foreground">or {formatPrice(proPlan.yearly_cents)}/year</span>
            </div>
            <ul className="mt-3 space-y-1.5 text-sm text-muted-foreground">
              {proPlan.features.slice(0, 4).map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <Check className="h-4 w-4 shrink-0 text-primary" />
                  {f}
                </li>
              ))}
            </ul>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Maybe later
            </Button>
            <Button
              onClick={() => handleUpgrade('pro', 'monthly')}
              disabled={!!checkoutPlan}
            >
              {checkoutPlan ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                copy.cta
              )}
            </Button>
          </div>

          <p className="text-center text-xs text-muted-foreground">
            <Link
              href="/pricing"
              className="underline hover:text-foreground"
              onClick={() => onOpenChange(false)}
            >
              Compare all plans
            </Link>
          </p>
        </div>
      </DialogContent>
    </Dialog>
  );
}
