'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  Loader2,
  CheckCircle,
  XCircle,
  Banknote,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

type PayoutItem = {
  id: string;
  creator_id: string;
  creator_email: string | null;
  amount_cents: number;
  status: string;
  payment_method: string;
  requested_at: string | null;
  approved_at: string | null;
  paid_at: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
};

export default function AdminCreatorPayoutsPage() {
  const { toast } = useToast();
  const [payouts, setPayouts] = useState<PayoutItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [acting, setActing] = useState<Record<string, boolean>>({});
  const [showAdjust, setShowAdjust] = useState<string | null>(null);
  const [adjustCreatorId, setAdjustCreatorId] = useState('');
  const [adjustAmount, setAdjustAmount] = useState('');
  const [adjustReason, setAdjustReason] = useState('');
  const [adjusting, setAdjusting] = useState(false);

  const fetchPayouts = () => {
    setLoading(true);
    const q = statusFilter ? `?status=${statusFilter}` : '';
    api<PayoutItem[]>(`/api/v1/admin/creator-payouts${q}`)
      .then(setPayouts)
      .catch(() => setPayouts([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPayouts();
  }, [statusFilter]);

  const handleApprove = async (id: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creator-payouts/${id}/approve`, { method: 'POST' });
      toast({ title: 'Payout approved' });
      fetchPayouts();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      toast({ title: err.detail || 'Failed', variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleReject = async (id: string, reason?: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creator-payouts/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ rejection_reason: reason || undefined }),
      });
      toast({ title: 'Payout rejected' });
      fetchPayouts();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      toast({ title: err.detail || 'Failed', variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleMarkPaid = async (id: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creator-payouts/${id}/mark-paid`, {
        method: 'POST',
        body: JSON.stringify({ payment_method: 'manual' }),
      });
      toast({ title: 'Payout marked as paid' });
      fetchPayouts();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      toast({ title: err.detail || 'Failed', variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleAdjustBalance = async () => {
    if (!adjustCreatorId || !adjustAmount) return;
    const cents = Math.round(parseFloat(adjustAmount || '0') * 100);
    if (cents === 0) {
      toast({ title: 'Enter a non-zero amount', variant: 'destructive' });
      return;
    }
    setAdjusting(true);
    try {
      await api(`/api/v1/admin/creator-payouts/adjust-balance/${adjustCreatorId}`, {
        method: 'POST',
        body: JSON.stringify({
          amount_cents: cents,
          reason: adjustReason || undefined,
        }),
      });
      toast({ title: 'Balance adjusted' });
      setShowAdjust(null);
      setAdjustCreatorId('');
      setAdjustAmount('');
      setAdjustReason('');
      fetchPayouts();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      toast({ title: err.detail || 'Failed', variant: 'destructive' });
    } finally {
      setAdjusting(false);
    }
  };

  const formatCents = (c: number) => `$${(c / 100).toFixed(2)}`;

  const statusBadge = (status: string) => {
    switch (status) {
      case 'paid':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded bg-green-500/10 text-green-600">
            <CheckCircle className="h-3 w-3" /> Paid
          </span>
        );
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded bg-blue-500/10 text-blue-600">
            Approved
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded bg-destructive/10 text-destructive">
            <XCircle className="h-3 w-3" /> Rejected
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded bg-amber-500/10 text-amber-600">
            Pending
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Creator payouts</h1>
        <p className="text-muted-foreground mt-1">
          Approve, reject, or mark payouts as paid. Adjust creator balances when needed.
        </p>
      </div>

      <div className="flex gap-2 items-center">
        <span className="text-sm text-muted-foreground">Filter:</span>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded border px-3 py-2 text-sm"
        >
          <option value="">All</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="paid">Paid</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Adjust creator balance</CardTitle>
            <CardDescription>
              Credit or debit a creator&apos;s balance (e.g. manual corrections).
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAdjust((s) => (s ? null : 'form'))}
          >
            {showAdjust ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            {showAdjust ? 'Hide' : 'Show'}
          </Button>
        </CardHeader>
        {showAdjust && (
          <CardContent className="space-y-4 border-t pt-4">
            <div className="flex flex-wrap gap-4 items-end">
              <div>
                <label className="text-sm font-medium">Creator ID (user_id)</label>
                <Input
                  className="mt-1 w-48"
                  placeholder="uuid"
                  value={adjustCreatorId}
                  onChange={(e) => setAdjustCreatorId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Amount ($)</label>
                <Input
                  type="number"
                  step="0.01"
                  className="mt-1 w-24"
                  placeholder="0.00"
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                />
                <p className="text-xs text-muted-foreground mt-0.5">Positive=credit, negative=debit</p>
              </div>
              <div>
                <label className="text-sm font-medium">Reason (optional)</label>
                <Input
                  className="mt-1 w-48"
                  placeholder="e.g. Manual correction"
                  value={adjustReason}
                  onChange={(e) => setAdjustReason(e.target.value)}
                />
              </div>
              <Button onClick={handleAdjustBalance} disabled={adjusting}>
                {adjusting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Banknote className="h-4 w-4" />}
                {adjusting ? ' Adjusting...' : ' Adjust'}
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Payout requests</CardTitle>
          <CardDescription>
            Creator payout requests. Approve to mark ready for payment, then mark paid when sent.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {payouts.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center">No payouts found.</p>
          ) : (
            <div className="space-y-4">
              {payouts.map((p) => (
                <div
                  key={p.id}
                  className="flex flex-wrap items-center justify-between gap-4 rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{formatCents(p.amount_cents)}</p>
                    <p className="text-sm text-muted-foreground">
                      {p.creator_email || p.creator_id} · Requested{' '}
                      {p.requested_at ? new Date(p.requested_at).toLocaleDateString() : '—'}
                    </p>
                    {p.rejection_reason && (
                      <p className="text-sm text-destructive mt-1">{p.rejection_reason}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {statusBadge(p.status)}
                    {p.status === 'pending' && (
                      <>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleApprove(p.id)}
                          disabled={acting[p.id]}
                        >
                          {acting[p.id] ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle className="h-4 w-4" />}
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleReject(p.id)}
                          disabled={acting[p.id]}
                        >
                          <XCircle className="h-4 w-4" /> Reject
                        </Button>
                      </>
                    )}
                    {(p.status === 'pending' || p.status === 'approved') && (
                      <Button
                        size="sm"
                        onClick={() => handleMarkPaid(p.id)}
                        disabled={acting[p.id]}
                      >
                        {acting[p.id] ? <Loader2 className="h-4 w-4 animate-spin" /> : <Banknote className="h-4 w-4" />}
                        Mark paid
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
