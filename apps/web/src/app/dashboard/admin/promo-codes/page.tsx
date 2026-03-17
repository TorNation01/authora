'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface PromoCode {
  id: string;
  code: string;
  plan_slug: string;
  discount_type: string;
  use_count: number;
  max_uses: number | null;
  revoked_at: string | null;
}

const PLAN_SLUGS = ['starter', 'pro', 'studio', 'founder_lifetime'];

export default function AdminPromoCodesPage() {
  const { toast } = useToast();
  const [codes, setCodes] = useState<PromoCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [includeRevoked, setIncludeRevoked] = useState(false);
  const [createCode, setCreateCode] = useState('');
  const [createPlan, setCreatePlan] = useState('pro');
  const [createDiscountType, setCreateDiscountType] = useState('free');
  const [createMaxUses, setCreateMaxUses] = useState<number | ''>(10);
  const [createDurationMonths, setCreateDurationMonths] = useState<number | ''>(6);
  const [createNote, setCreateNote] = useState('');
  const [creating, setCreating] = useState(false);

  const fetchCodes = useCallback(() => {
    setLoading(true);
    api<PromoCode[]>(`/api/v1/billing/admin/promo-codes?include_revoked=${includeRevoked}`)
      .then(setCodes)
      .catch(() => {
        toast({ title: 'Failed to load codes', variant: 'destructive' });
        setCodes([]);
      })
      .finally(() => setLoading(false));
  }, [includeRevoked, toast]);

  useEffect(() => {
    fetchCodes();
  }, [fetchCodes]);

  const handleCreate = async () => {
    if (!createCode.trim()) {
      toast({ title: 'Enter a code', variant: 'destructive' });
      return;
    }
    setCreating(true);
    try {
      await api('/api/v1/billing/admin/promo-codes', {
        method: 'POST',
        body: JSON.stringify({
          code: createCode.trim().toUpperCase(),
          plan_slug: createPlan,
          discount_type: createDiscountType,
          duration_months: createDurationMonths || undefined,
          max_uses: createMaxUses || undefined,
          internal_note: createNote || undefined,
        }),
      });
      toast({ title: 'Code created' });
      setCreateCode('');
      fetchCodes();
    } catch {
      toast({ title: 'Failed to create code', variant: 'destructive' });
    } finally {
      setCreating(false);
    }
  };

  const revokeCode = async (codeId: string) => {
    try {
      await api(`/api/v1/billing/admin/promo-codes/${codeId}/revoke`, { method: 'POST' });
      toast({ title: 'Code revoked' });
      fetchCodes();
    } catch {
      toast({ title: 'Failed to revoke', variant: 'destructive' });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Special access codes</h1>
          <p className="mt-1 text-muted-foreground">
            Create codes for tier, free or discounted access, duration, and redemption tracking.
          </p>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href="/dashboard/admin/grants">Entitlement grants</Link>
        </Button>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Create access code</h2>
          <p className="text-sm text-muted-foreground">Code string, tier granted, duration, max uses. Redemption tracking included.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Code string</Label>
              <Input
                value={createCode}
                onChange={(e) => setCreateCode(e.target.value.toUpperCase())}
                placeholder="e.g. FOUNDER50"
              />
            </div>
            <div>
              <Label>Tier granted</Label>
              <Select value={createPlan} onValueChange={setCreatePlan}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  {PLAN_SLUGS.map((s) => (
                    <SelectItem key={s} value={s}>{s}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Free or discounted access</Label>
              <Select value={createDiscountType} onValueChange={setCreateDiscountType}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="free">Free</SelectItem>
                  <SelectItem value="percentage">Percentage</SelectItem>
                  <SelectItem value="fixed">Fixed</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Max uses</Label>
              <Input
                type="number"
                min={1}
                placeholder="Unlimited"
                value={createMaxUses}
                onChange={(e) => setCreateMaxUses(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
              />
            </div>
            <div>
              <Label>Duration (months)</Label>
              <Input
                type="number"
                min={1}
                placeholder="Lifetime if empty"
                value={createDurationMonths}
                onChange={(e) => setCreateDurationMonths(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
              />
            </div>
            <div>
              <Label>Internal Notes</Label>
              <Input value={createNote} onChange={(e) => setCreateNote(e.target.value)} placeholder="Optional" />
            </div>
          </div>
          <Button onClick={handleCreate} disabled={creating}>
            {creating ? 'Creating…' : 'Create code'}
          </Button>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
            <div className="flex items-center justify-between">
            <h2 className="font-semibold">Codes (redemption tracking)</h2>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={includeRevoked}
                onChange={(e) => setIncludeRevoked(e.target.checked)}
              />
              Include revoked
            </label>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading...</p>
          ) : codes.length === 0 ? (
            <p className="text-muted-foreground">No promo codes.</p>
          ) : (
            <div className="overflow-x-auto rounded-lg border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="px-4 py-3 text-left font-medium">Code</th>
                    <th className="px-4 py-3 text-left font-medium">Tier</th>
                    <th className="px-4 py-3 text-left font-medium">Uses</th>
                    <th className="px-4 py-3 text-left font-medium">Status</th>
                    <th className="px-4 py-3 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {codes.map((c) => (
                    <tr key={c.id} className="border-b last:border-0">
                      <td className="px-4 py-3 font-mono font-medium">{c.code}</td>
                      <td className="px-4 py-3 text-muted-foreground">{c.plan_slug}</td>
                      <td className="px-4 py-3 text-muted-foreground">
                        {c.use_count}
                        {c.max_uses != null ? ` / ${c.max_uses}` : ''}
                      </td>
                      <td className="px-4 py-3">
                        {c.revoked_at ? (
                          <span className="text-destructive">Revoked</span>
                        ) : (
                          <span className="text-muted-foreground">Active</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {!c.revoked_at && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => revokeCode(c.id)}
                          >
                            Revoke
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
