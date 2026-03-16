'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Lock, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getBillingStatus, type BillingStatus } from '@/lib/billing';

interface FeatureGateProps {
  feature: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  upgradeMessage?: string;
}

export function FeatureGate({ feature, children, fallback, upgradeMessage }: FeatureGateProps) {
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getBillingStatus()
      .then(setStatus)
      .finally(() => setLoading(false));
  }, []);

  if (loading || !status) return null;
  if (status.billing_exempt) return <>{children}</>;
  if (status.plan.features.includes(feature)) return <>{children}</>;

  if (fallback) return <>{fallback}</>;

  return (
    <div className="rounded-lg border border-dashed border-muted-foreground/30 bg-muted/30 p-6 text-center">
      <Lock className="mx-auto h-10 w-10 text-muted-foreground" />
      <p className="mt-2 font-medium">{upgradeMessage ?? 'This feature requires a paid plan.'}</p>
      <Button asChild variant="outline" size="sm" className="mt-3">
        <Link href="/pricing">
          <Sparkles className="h-4 w-4 mr-2" />
          Upgrade
        </Link>
      </Button>
    </div>
  );
}
