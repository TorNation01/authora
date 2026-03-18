'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Package, CreditCard, TrendingUp } from 'lucide-react';
import Link from 'next/link';

type TemplatePack = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  price_cents: number;
  stripe_price_id: string | null;
  template_slugs: string[];
  sort_order: number;
  is_active: boolean;
  is_featured?: boolean;
  creator_id: string | null;
  revenue_share_pct: number | null;
  created_at: string | null;
};

export default function AdminTemplatePacksPage() {
  const { toast } = useToast();
  const [packs, setPacks] = useState<TemplatePack[]>([]);
  const [analytics, setAnalytics] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [includeInactive, setIncludeInactive] = useState(false);

  useEffect(() => {
    Promise.all([
      api<{ packs: TemplatePack[] }>(`/api/v1/admin/template-packs?include_inactive=${includeInactive}`),
      api<{ by_pack: Record<string, number> }>('/api/v1/admin/template-packs/analytics').catch(() => ({ by_pack: {} })),
    ]).then(([packsRes, analyticsRes]) => {
      setPacks(packsRes.packs);
      setAnalytics(analyticsRes.by_pack || {});
    }).catch(() => setPacks([])).finally(() => setLoading(false));
  }, [includeInactive]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Template packs</h1>
          <p className="text-muted-foreground mt-1">
            Manage template packs: pricing, visibility, Stripe. Packs are seeded from template_pack_definitions.py.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={includeInactive}
              onChange={(e) => setIncludeInactive(e.target.checked)}
              className="rounded"
            />
            Include inactive
          </label>
          <Button variant="outline" asChild>
            <Link href="/dashboard/billing">
              <CreditCard className="h-4 w-4 mr-2" />
              View billing
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {packs.map((p) => (
            <Card key={p.id} variant="soft" className={!p.is_active ? 'opacity-70' : ''}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <Package className="h-5 w-5 text-primary" />
                    <h2 className="font-semibold">{p.name}</h2>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {p.is_featured && (
                      <Badge variant="default" className="text-xs">Featured</Badge>
                    )}
                    {!p.is_active && (
                      <Badge variant="secondary" className="text-xs">Inactive</Badge>
                    )}
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">{p.slug}</p>
              </CardHeader>
              <CardContent className="space-y-3">
                {p.description && (
                  <p className="text-sm line-clamp-2">{p.description}</p>
                )}
                <div className="flex items-center gap-4 text-sm">
                  <span className="font-medium">${(p.price_cents / 100).toFixed(2)}</span>
                  {p.stripe_price_id ? (
                    <Badge variant="outline" className="text-xs">Stripe configured</Badge>
                  ) : (
                    <Badge variant="secondary" className="text-xs">No Stripe price</Badge>
                  )}
                  {analytics[p.slug] !== undefined && (
                    <span className="flex items-center gap-1 text-muted-foreground">
                      <TrendingUp className="h-3.5 w-3.5" />
                      {analytics[p.slug]} purchases
                    </span>
                  )}
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-medium text-muted-foreground">
                    Templates ({p.template_slugs?.length || 0})
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {p.template_slugs?.slice(0, 5).map((s) => (
                      <span key={s} className="rounded bg-muted px-1.5 py-0.5 text-xs font-mono">
                        {s}
                      </span>
                    ))}
                    {(p.template_slugs?.length || 0) > 5 && (
                      <span className="text-xs text-muted-foreground">
                        +{(p.template_slugs?.length || 0) - 5} more
                      </span>
                    )}
                  </div>
                </div>
                {p.revenue_share_pct != null && (
                  <p className="text-xs text-muted-foreground">
                    Revenue share: {p.revenue_share_pct}%
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Card variant="soft">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Packs are managed via <code className="rounded bg-muted px-1">template_pack_definitions.py</code> and{' '}
            <code className="rounded bg-muted px-1">seed_template_packs</code>. To create or edit packs via API:{' '}
            <code className="rounded bg-muted px-1">POST /api/v1/admin/template-packs</code>,{' '}
            <code className="rounded bg-muted px-1">PATCH /api/v1/admin/template-packs/:id</code>.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
