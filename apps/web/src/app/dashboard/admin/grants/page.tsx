'use client';

import { useCallback, useEffect, useState } from 'react';
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
const REASONS = ['family', 'founder', 'beta_tester', 'partner', 'internal_use', 'scholarship', 'support_resolution', 'custom'];
const ON_EXPIRY = ['revert_previous', 'revert_free', 'prompt_billing'];
const ACCESS_TYPES = ['paid', 'discounted', 'free'];

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
  const [createDurationMonths, setCreateDurationMonths] = useState<number | ''>(6);
  const [createNotes, setCreateNotes] = useState('');
  const [creating, setCreating] = useState(false);

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
    setCreating(true);
    try {
      await api('/api/v1/billing/admin/grants', {
        method: 'POST',
        body: JSON.stringify({
          user_id: selectedUserId,
          plan_slug: createPlan,
          duration_months: createDurationMonths || undefined,
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Entitlement grants</h1>
        <p className="mt-1 text-muted-foreground">Grant users access to plans manually. Grants override Stripe when configured.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Grant access</h2>
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
                  <Label>Plan</Label>
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
                  <Label>Duration (months)</Label>
                  <Input
                    type="number"
                    min={1}
                    placeholder="e.g. 6 or leave empty for lifetime"
                    value={createDurationMonths}
                    onChange={(e) => setCreateDurationMonths(e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                  />
                </div>
                <div>
                  <Label>Reason</Label>
                  <Select value={createReason} onValueChange={setCreateReason}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {REASONS.map((r) => (
                        <SelectItem key={r} value={r}>{r}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Access type</Label>
                  <Select value={createAccessType} onValueChange={setCreateAccessType}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {ACCESS_TYPES.map((a) => (
                        <SelectItem key={a} value={a}>{a}</SelectItem>
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
                  <Label>On expiry</Label>
                  <Select value={createOnExpiry} onValueChange={setCreateOnExpiry}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {ON_EXPIRY.map((o) => (
                        <SelectItem key={o} value={o}>{o}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Internal notes</Label>
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
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-muted-foreground">Loading...</p>
            ) : grants.length === 0 ? (
              <p className="text-muted-foreground">No grants for this user.</p>
            ) : (
              <div className="space-y-2">
                {grants.map((g) => (
                  <div key={g.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <span className="font-medium">{g.plan_slug}</span>
                      <span className="mx-2 text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground">{g.reason}</span>
                      {g.expires_at && (
                        <span className="ml-2 text-sm">expires {new Date(g.expires_at).toLocaleDateString()}</span>
                      )}
                      {g.revoked_at && (
                        <span className="ml-2 text-sm text-destructive">revoked</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      {!g.revoked_at && !g.expires_at && (
                        <Button variant="outline" size="sm" onClick={() => convertToLifetime(g.id)}>
                          Convert to lifetime
                        </Button>
                      )}
                      {!g.revoked_at && (
                        <Button variant="outline" size="sm" onClick={() => revokeGrant(g.id)}>
                          Revoke
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
