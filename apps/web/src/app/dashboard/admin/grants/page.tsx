'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface Grant {
  id: string;
  user_id: string;
  plan_slug: string;
  granted_at: string;
  expires_at: string | null;
  reason: string;
  access_type: string;
  override_stripe: boolean;
  on_expiry: string;
  revoked_at: string | null;
}

const PLAN_SLUGS = ['free', 'starter', 'pro', 'studio', 'founder_lifetime'];
const REASON_LABELS: Record<string, string> = {
  family: 'Family',
  founder: 'Founder',
  beta_tester: 'Beta tester',
  partner: 'Partner',
  internal_use: 'Internal use',
  scholarship: 'Scholarship',
  support_resolution: 'Support resolution',
  custom: 'Custom',
};
const ON_EXPIRY_LABELS: Record<string, string> = {
  revert_previous: 'Revert to previous plan',
  revert_free: 'Revert to Free',
  prompt_billing: 'Prompt for billing',
};
const ACCESS_TYPE_LABELS: Record<string, string> = {
  paid: 'Paid',
  discounted: 'Discounted',
  free: 'Complimentary Access',
};
const DURATION_OPTIONS: { value: string; label: string; months?: number; years?: number }[] = [
  { value: 'lifetime', label: 'Lifetime Access' },
  { value: '12', label: '12 months', months: 12 },
  { value: '6', label: '6 months', months: 6 },
  { value: '3', label: '3 months', months: 3 },
  { value: '1', label: '1 month', months: 1 },
  { value: 'custom', label: 'Custom' },
];

export default function AdminGrantsPage() {
  const { toast } = useToast();
  const [grants, setGrants] = useState<Grant[]>([]);
  const [userSearch, setUserSearch] = useState('');
  const [selectedUserId, setSelectedUserId] = useState('');
  const [users, setUsers] = useState<{ id: string; email: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [createPlan, setCreatePlan] = useState('pro');
  const [createReason, setCreateReason] = useState('support_resolution');
  const [createAccessType, setCreateAccessType] = useState('free');
  const [createOverrideStripe, setCreateOverrideStripe] = useState(true);
  const [createOnExpiry, setCreateOnExpiry] = useState('revert_free');
  const [createDuration, setCreateDuration] = useState('6');
  const [createDurationMonths, setCreateDurationMonths] = useState<number | ''>(6);
  const [createNotes, setCreateNotes] = useState('');
  const [creating, setCreating] = useState(false);
  const [extendGrantId, setExtendGrantId] = useState<string | null>(null);
  const [extendNewDate, setExtendNewDate] = useState('');
  const [extending, setExtending] = useState(false);

  const fetchGrants = useCallback(async (userId: string) => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await api<Grant[]>(`/api/v1/billing/admin/grants/${userId}?include_revoked=true`);
      setGrants(data);
    } catch {
      toast({ title: 'Failed to load grants', variant: 'destructive' });
      setGrants([]);
    } finally {
      setLoading(false);
    }
  }, [toast]);

  const searchUsers = useCallback(async () => {
    if (!userSearch.trim()) return;
    try {
      const data = await api<{ users: { id: string; email: string }[] }>(`/api/v1/admin/users?search=${encodeURIComponent(userSearch)}&limit=20`);
      setUsers(data.users || []);
    } catch {
      setUsers([]);
    }
  }, [userSearch]);

  useEffect(() => {
    if (selectedUserId) fetchGrants(selectedUserId);
    else setGrants([]);
  }, [selectedUserId, fetchGrants]);

  const handleCreateGrant = async () => {
    if (!selectedUserId) {
      toast({ title: 'Select a user first', variant: 'destructive' });
      return;
    }
    const opt = DURATION_OPTIONS.find((d) => d.value === createDuration);
    const durationMonths = createDuration === 'custom' ? createDurationMonths : opt?.months;
    const durationYears = opt?.years;
    setCreating(true);
    try {
      await api('/api/v1/billing/admin/grants', {
        method: 'POST',
        body: JSON.stringify({
          user_id: selectedUserId,
          plan_slug: createPlan,
          duration_months: createDuration === 'lifetime' ? undefined : durationMonths || undefined,
          duration_years: durationYears,
          reason: createReason,
          access_type: createAccessType,
          override_stripe: createOverrideStripe,
          on_expiry: createOnExpiry,
          internal_notes: createNotes || undefined,
        }),
      });
      toast({ title: 'Grant created' });
      fetchGrants(selectedUserId);
    } catch (e: unknown) {
      toast({ title: 'Failed to create grant', variant: 'destructive' });
    } finally {
      setCreating(false);
    }
  };

  const revokeGrant = async (grantId: string) => {
    try {
      await api(`/api/v1/billing/admin/grants/${grantId}/revoke`, { method: 'POST' });
      toast({ title: 'Grant revoked' });
      if (selectedUserId) fetchGrants(selectedUserId);
    } catch {
      toast({ title: 'Failed to revoke', variant: 'destructive' });
    }
  };

  const convertToLifetime = async (grantId: string) => {
    try {
      await api(`/api/v1/billing/admin/grants/${grantId}/convert-lifetime`, { method: 'POST' });
      toast({ title: 'Converted to lifetime' });
      if (selectedUserId) fetchGrants(selectedUserId);
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    }
  };

  const openExtendDialog = (grant: Grant) => {
    setExtendGrantId(grant.id);
    setExtendNewDate(
      grant.expires_at
        ? new Date(grant.expires_at).toISOString().slice(0, 10)
        : new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
    );
  };

  const handleExtendGrant = async () => {
    if (!extendGrantId || !extendNewDate) return;
    setExtending(true);
    try {
      const iso = new Date(extendNewDate + 'T23:59:59.999Z').toISOString();
      await api(`/api/v1/billing/admin/grants/${extendGrantId}/extend`, {
        method: 'POST',
        body: JSON.stringify({ new_expires_at: iso }),
      });
      toast({ title: 'Grant extended' });
      setExtendGrantId(null);
      if (selectedUserId) fetchGrants(selectedUserId);
    } catch {
      toast({ title: 'Failed to extend', variant: 'destructive' });
    } finally {
      setExtending(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Entitlement grants</h1>
          <p className="mt-1 text-muted-foreground">
            Manual access grants. Assign tier, duration, and reason.
          </p>
        </div>
        <Button asChild variant="outline" size="sm">
          <Link href="/dashboard/admin/promo-codes">Special access codes</Link>
        </Button>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Manual Access Grants</h2>
          <p className="text-sm text-muted-foreground">Assign tier manually. Choose paid, discounted, or fully free access.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search user by email..."
              value={userSearch}
              onChange={(e) => setUserSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchUsers()}
            />
            <Button variant="outline" onClick={searchUsers}>Search</Button>
          </div>
          {users.length > 0 && (
            <div className="space-y-2">
              <Label>Select user</Label>
              <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Choose user" />
                </SelectTrigger>
                <SelectContent>
                  {users.map((u) => (
                    <SelectItem key={u.id} value={u.id}>{u.email}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          {selectedUserId && (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Plan Override</Label>
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
                  <Label>Duration</Label>
                  <Select value={createDuration} onValueChange={setCreateDuration}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {DURATION_OPTIONS.map((d) => (
                        <SelectItem key={d.value} value={d.value}>{d.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {createDuration === 'custom' && (
                    <Input
                      type="number"
                      min={1}
                      className="mt-2"
                      placeholder="Months"
                      value={createDurationMonths}
                      onChange={(e) => setCreateDurationMonths(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                    />
                  )}
                </div>
                <div>
                  <Label>Grant Reason</Label>
                  <Select value={createReason} onValueChange={setCreateReason}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(REASON_LABELS).map(([v, l]) => (
                        <SelectItem key={v} value={v}>{l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Access Type</Label>
                  <Select value={createAccessType} onValueChange={setCreateAccessType}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(ACCESS_TYPE_LABELS).map(([v, l]) => (
                        <SelectItem key={v} value={v}>{l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Override Stripe</Label>
                  <Select value={String(createOverrideStripe)} onValueChange={(v) => setCreateOverrideStripe(v === 'true')}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="true">Yes</SelectItem>
                      <SelectItem value="false">No</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>On Expiry</Label>
                  <Select value={createOnExpiry} onValueChange={setCreateOnExpiry}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {Object.entries(ON_EXPIRY_LABELS).map(([v, l]) => (
                        <SelectItem key={v} value={v}>{l}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Internal Notes</Label>
                <Input value={createNotes} onChange={(e) => setCreateNotes(e.target.value)} placeholder="Optional" />
              </div>
              <Button onClick={handleCreateGrant} disabled={creating}>
                {creating ? 'Creating…' : 'Create grant'}
              </Button>
            </>
          )}
        </CardContent>
      </Card>

      {selectedUserId && (
        <Card variant="soft">
          <CardHeader>
            <h2 className="font-semibold">Grant history</h2>
            <p className="text-sm text-muted-foreground">
              Revoke or extend grants. Convert temporary to Lifetime Access.
            </p>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : grants.length === 0 ? (
              <p className="text-muted-foreground">No grants for this user.</p>
            ) : (
              <div className="overflow-x-auto rounded-lg border">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-4 py-3 text-left font-medium">Plan</th>
                      <th className="px-4 py-3 text-left font-medium">Reason</th>
                      <th className="px-4 py-3 text-left font-medium">Expires</th>
                      <th className="px-4 py-3 text-left font-medium">Status</th>
                      <th className="px-4 py-3 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {grants.map((g) => (
                      <tr key={g.id} className="border-b last:border-0">
                        <td className="px-4 py-3 font-medium">{g.plan_slug}</td>
                        <td className="px-4 py-3 text-muted-foreground">{g.reason}</td>
                        <td className="px-4 py-3 text-muted-foreground">
                          {g.expires_at
                            ? new Date(g.expires_at).toLocaleDateString()
                            : 'Lifetime'}
                        </td>
                        <td className="px-4 py-3">
                          {g.revoked_at ? (
                            <span className="text-destructive">Revoked</span>
                          ) : (
                            <span className="text-muted-foreground">Active</span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right">
                          {!g.revoked_at && (
                            <div className="flex justify-end gap-2">
                              {g.expires_at && (
                                <>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => openExtendDialog(g)}
                                  >
                                    Extend
                                  </Button>
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => convertToLifetime(g.id)}
                                  >
                                    Convert to Lifetime
                                  </Button>
                                </>
                              )}
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => revokeGrant(g.id)}
                              >
                                Revoke
                              </Button>
                            </div>
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
      )}

      <Dialog open={!!extendGrantId} onOpenChange={(open) => !open && setExtendGrantId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Extend grant</DialogTitle>
            <DialogDescription>Set a new expiry date for this access grant.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Label htmlFor="extend-date">New expiry date</Label>
            <Input
              id="extend-date"
              type="date"
              value={extendNewDate}
              onChange={(e) => setExtendNewDate(e.target.value)}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setExtendGrantId(null)}>
              Cancel
            </Button>
            <Button onClick={handleExtendGrant} disabled={extending}>
              {extending ? 'Extending…' : 'Extend'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
