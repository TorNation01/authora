'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { BarChart3, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { getBillingStatus, type BillingStatus } from '@/lib/billing';

export function UsageDisplay() {
  const [status, setStatus] = useState<BillingStatus | null>(null);

  useEffect(() => {
    getBillingStatus().then(setStatus);
  }, []);

  if (!status || status.billing_exempt) return null;
  if (status.plan.slug === 'premium' && status.usage.ai_actions < 400) return null;

  const aiPct = status.usage.ai_actions_limit > 0
    ? Math.min(100, (status.usage.ai_actions / status.usage.ai_actions_limit) * 100)
    : 0;
  const exportPct = status.usage.exports_limit > 0
    ? Math.min(100, (status.usage.exports / status.usage.exports_limit) * 100)
    : 0;

  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-medium flex items-center gap-2">
          <BarChart3 className="h-4 w-4" />
          Your usage
        </h3>
        {status.can_upgrade && (
          <Button asChild variant="ghost" size="sm">
            <Link href="/pricing">
              <Sparkles className="h-3.5 w-3.5 mr-1" />
              Upgrade
            </Link>
          </Button>
        )}
      </div>
      <div className="mt-3 space-y-2 text-sm">
        <div>
          <span className="text-muted-foreground">AI actions</span>
          <span className="float-right">{status.usage.ai_actions} / {status.usage.ai_actions_limit}</span>
          <Progress value={aiPct} size="sm" className="mt-1" />
        </div>
        <div>
          <span className="text-muted-foreground">Exports</span>
          <span className="float-right">{status.usage.exports} / {status.usage.exports_limit}</span>
          <Progress value={exportPct} size="sm" className="mt-1" />
        </div>
      </div>
    </div>
  );
}
