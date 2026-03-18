'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, DollarSign, Wallet, ArrowUpRight, ArrowDownLeft, Clock, CheckCircle, XCircle } from 'lucide-react';

type PayoutItem = {
  id: string;
  amount_cents: number;
  status: string;
  payment_method: string;
  requested_at: string | null;
  approved_at: string | null;
  paid_at: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
};

type EarningsData = {
  available_balance_cents: number;
  total_earned_cents: number;
  total_adjustments_cents: number;
  total_paid_cents: number;
  min_payout_cents: number;
  payouts: PayoutItem[];
};

export default function CreatorEarningsPage() {
  const { toast } = useToast();
  const [data, setData] = useState<EarningsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [requesting, setRequesting] = useState(false);
  const [amountCents, setAmountCents] = useState('');

  const fetchEarnings = () => {
    api<EarningsData>('/api/v1/creators/earnings')
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchEarnings();
  }, []);

  const handleRequestPayout = async () => {
    const cents = Math.round(parseFloat(amountCents || '0') * 100);
    if (cents < 1) {
      toast({ title: 'Enter a valid amount', variant: 'destructive' });
      return;
    }
    setRequesting(true);
    try {
      await api('/api/v1/creators/payout', {
        method: 'POST',
        body: JSON.stringify({ amount_cents: cents }),
      });
      toast({ title: 'Payout requested', description: 'Your request has been submitted for review.' });
      setAmountCents('');
      fetchEarnings();
    } catch (e: unknown) {
      const err = e as { detail?: string };
      toast({ title: err.detail || 'Request failed', variant: 'destructive' });
    } finally {
      setRequesting(false);
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
            <Clock className="h-3 w-3" /> Approved
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
            <Clock className="h-3 w-3" /> Pending
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

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Earnings</h1>
        <p className="text-muted-foreground">Unable to load earnings data.</p>
      </div>
    );
  }

  const canRequest = data.available_balance_cents >= data.min_payout_cents;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Earnings</h1>
        <p className="text-muted-foreground mt-1">
          Your balance, payout history, and request payouts.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Available balance</CardTitle>
            <Wallet className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCents(data.available_balance_cents)}</div>
            <p className="text-xs text-muted-foreground">
              Ready to withdraw
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total earned</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCents(data.total_earned_cents)}</div>
            <p className="text-xs text-muted-foreground">
              From template sales
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Adjustments</CardTitle>
            <ArrowDownLeft className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCents(data.total_adjustments_cents)}</div>
            <p className="text-xs text-muted-foreground">
              Credits / debits
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total paid out</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCents(data.total_paid_cents)}</div>
            <p className="text-xs text-muted-foreground">
              Payouts completed
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Request payout</CardTitle>
          <CardDescription>
            Minimum payout: {formatCents(data.min_payout_cents)}. Enter amount in dollars.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2 max-w-xs">
            <Input
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              value={amountCents}
              onChange={(e) => setAmountCents(e.target.value)}
            />
            <Button
              onClick={handleRequestPayout}
              disabled={!canRequest || requesting}
            >
              {requesting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Requesting...
                </>
              ) : (
                'Request payout'
              )}
            </Button>
          </div>
          {!canRequest && (
            <p className="text-sm text-muted-foreground">
              You need at least {formatCents(data.min_payout_cents)} available to request a payout.
            </p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Payout history</CardTitle>
          <CardDescription>
            Your payout requests and their status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {data.payouts.length === 0 ? (
            <p className="text-muted-foreground py-8 text-center">
              No payouts yet.
            </p>
          ) : (
            <div className="space-y-3">
              {data.payouts.map((p) => (
                <div
                  key={p.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{formatCents(p.amount_cents)}</p>
                    <p className="text-sm text-muted-foreground">
                      Requested {p.requested_at ? new Date(p.requested_at).toLocaleDateString() : '—'}
                      {p.paid_at && ` · Paid ${new Date(p.paid_at).toLocaleDateString()}`}
                      {p.rejected_at && ` · Rejected ${new Date(p.rejected_at).toLocaleDateString()}`}
                    </p>
                    {p.rejection_reason && (
                      <p className="text-sm text-destructive mt-1">{p.rejection_reason}</p>
                    )}
                  </div>
                  {statusBadge(p.status)}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
