'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { getBillingStatus, type BillingStatus } from '@/lib/billing';
import { useConfig } from '@/contexts/ConfigProvider';

interface UpgradeCalloutProps {
  /** Feature that requires upgrade (e.g. 'ghostwriter', 'export_pdf') */
  feature?: string;
  /** Custom message */
  message?: string;
  /** Compact variant for inline use */
  compact?: boolean;
}

export function UpgradeCallout({ feature, message, compact }: UpgradeCalloutProps) {
  const config = useConfig();
  const [status, setStatus] = useState<BillingStatus | null>(null);

  useEffect(() => {
    getBillingStatus()
      .then(setStatus)
      .catch(() => setStatus(null));
  }, []);

  if (!config.feature_flags.billing) return null;
  if (!status) return null;
  if (status.billing_exempt) return null;
  if (!status.can_upgrade) return null;

  const hasFeature = feature ? status.plan.features.includes(feature) : true;
  if (feature && hasFeature) return null;

  const defaultMessage = feature
    ? 'This feature requires a paid plan.'
    : 'Upgrade for more projects, AI, and premium features.';

  if (compact) {
    return (
      <Button asChild variant="outline" size="sm">
        <Link href="/pricing">
          <Sparkles className="h-3.5 w-3.5 mr-1.5" />
          Upgrade
        </Link>
      </Button>
    );
  }

  return (
    <div className="rounded-lg border border-dashed border-primary/40 bg-primary/5 p-4">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground">
          {message ?? defaultMessage}
        </p>
        <Button asChild size="sm">
          <Link href="/pricing">
            <Sparkles className="h-4 w-4 mr-2" />
            Upgrade
          </Link>
        </Button>
      </div>
    </div>
  );
}
