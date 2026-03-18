'use client';

import { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { CreditCard, Loader2, CheckCircle, AlertCircle, ExternalLink, Wallet } from 'lucide-react';
import Link from 'next/link';

type PaymentSettings = {
  stripe_configured: boolean;
  webhook_secret_set: boolean;
  live_mode: boolean | null;
  feature_billing: boolean;
  plans_count: number;
  plans_with_stripe_prices: number;
  stripe_success_url: string;
  stripe_cancel_url: string;
  paypal_configured: boolean;
  paypal_mode: string;
};

export default function AdminPaymentsPage() {
  const { toast } = useToast();
  const [data, setData] = useState<PaymentSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    stripe_secret_key: '',
    stripe_publishable_key: '',
    stripe_webhook_secret: '',
    stripe_success_url: '',
    stripe_cancel_url: '',
    feature_billing: false,
    paypal_client_id: '',
    paypal_client_secret: '',
    paypal_mode: 'sandbox',
  });

  const fetchSettings = useCallback(() => {
    setLoading(true);
    api<PaymentSettings>('/api/v1/admin/payment-settings')
      .then((d) => {
        setData(d);
        setForm((f) => ({
          ...f,
          stripe_success_url: d.stripe_success_url || '',
          stripe_cancel_url: d.stripe_cancel_url || '',
          feature_billing: d.feature_billing,
          paypal_mode: d.paypal_mode || 'sandbox',
        }));
      })
      .catch(() => toast({ title: 'Failed to load payment settings', variant: 'destructive' }))
      .finally(() => setLoading(false));
  }, [toast]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: Record<string, string | boolean> = {};
      if (form.stripe_secret_key.trim()) payload.stripe_secret_key = form.stripe_secret_key.trim();
      if (form.stripe_publishable_key.trim())
        payload.stripe_publishable_key = form.stripe_publishable_key.trim();
      if (form.stripe_webhook_secret.trim())
        payload.stripe_webhook_secret = form.stripe_webhook_secret.trim();
      if (form.stripe_success_url.trim()) payload.stripe_success_url = form.stripe_success_url.trim();
      if (form.stripe_cancel_url.trim()) payload.stripe_cancel_url = form.stripe_cancel_url.trim();
      payload.feature_billing = form.feature_billing;
      if (form.paypal_client_id.trim()) payload.paypal_client_id = form.paypal_client_id.trim();
      if (form.paypal_client_secret.trim()) payload.paypal_client_secret = form.paypal_client_secret.trim();
      if (form.paypal_mode) payload.paypal_mode = form.paypal_mode;

      await api('/api/v1/admin/payment-settings', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });
      toast({ title: 'Payment settings saved', description: 'Restart the API for changes to take effect.' });
      setForm((f) => ({
        ...f,
        stripe_secret_key: '',
        stripe_publishable_key: '',
        stripe_webhook_secret: '',
        paypal_client_id: '',
        paypal_client_secret: '',
      }));
      fetchSettings();
    } catch {
      toast({ title: 'Failed to save', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="w-full min-w-0 max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Payment settings</h1>
        <p className="text-muted-foreground mt-1">
          Configure Stripe and PayPal to receive payments for subscriptions and template purchases.
        </p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Current status
          </h2>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="flex items-center gap-2 rounded border p-3">
              {data?.stripe_configured ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-amber-600" />
              )}
              <div>
                <p className="font-medium">Stripe</p>
                <p className="text-sm text-muted-foreground">
                  {data?.stripe_configured ? 'Configured' : 'Not configured'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded border p-3">
              {data?.webhook_secret_set ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-amber-600" />
              )}
              <div>
                <p className="font-medium">Webhook secret</p>
                <p className="text-sm text-muted-foreground">
                  {data?.webhook_secret_set ? 'Set' : 'Not set'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded border p-3">
              <div>
                <p className="font-medium">Mode</p>
                <p className="text-sm text-muted-foreground">
                  {data?.live_mode === true ? 'Live' : data?.live_mode === false ? 'Test' : '—'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded border p-3">
              <div>
                <p className="font-medium">Billing feature</p>
                <p className="text-sm text-muted-foreground">
                  {data?.feature_billing ? 'Enabled' : 'Disabled'}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 rounded border p-3 sm:col-span-2">
              <div>
                <p className="font-medium">Plans with Stripe prices</p>
                <p className="text-sm text-muted-foreground">
                  {data?.plans_with_stripe_prices ?? 0} of {data?.plans_count ?? 0} plans have
                  Stripe price IDs
                </p>
              </div>
              <Button variant="outline" size="sm" asChild>
                <Link href="/dashboard/admin/template-packs">Template packs</Link>
              </Button>
            </div>
            <div className="flex items-center gap-2 rounded border p-3">
              {data?.paypal_configured ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertCircle className="h-5 w-5 text-amber-600" />
              )}
              <div>
                <p className="font-medium">PayPal</p>
                <p className="text-sm text-muted-foreground">
                  {data?.paypal_configured ? 'Configured' : 'Not configured'}
                </p>
              </div>
            </div>
            {data?.paypal_configured && (
              <div className="flex items-center gap-2 rounded border p-3">
                <div>
                  <p className="font-medium">PayPal mode</p>
                  <p className="text-sm text-muted-foreground">
                    {data?.paypal_mode === 'live' ? 'Live' : 'Sandbox'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Configure Stripe</h2>
          <p className="text-sm text-muted-foreground">
            Add your Stripe API keys from the{' '}
            <a
              href="https://dashboard.stripe.com/apikeys"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline inline-flex items-center gap-1"
            >
              Stripe Dashboard
              <ExternalLink className="h-3 w-3" />
            </a>
            . Leave fields blank to keep existing values.
          </p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">Secret key (sk_live_ or sk_test_)</label>
              <Input
                type="password"
                placeholder="sk_..."
                value={form.stripe_secret_key}
                onChange={(e) => setForm((f) => ({ ...f, stripe_secret_key: e.target.value }))}
                className="mt-1 font-mono"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Publishable key (pk_live_ or pk_test_)</label>
              <Input
                type="password"
                placeholder="pk_..."
                value={form.stripe_publishable_key}
                onChange={(e) => setForm((f) => ({ ...f, stripe_publishable_key: e.target.value }))}
                className="mt-1 font-mono"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Webhook signing secret (whsec_)</label>
              <Input
                type="password"
                placeholder="whsec_..."
                value={form.stripe_webhook_secret}
                onChange={(e) => setForm((f) => ({ ...f, stripe_webhook_secret: e.target.value }))}
                className="mt-1 font-mono"
                autoComplete="off"
              />
              <p className="text-xs text-muted-foreground mt-1">
                Create a webhook in Stripe pointing to{' '}
                <code className="rounded bg-muted px-1">
                  {(
                    (typeof window !== 'undefined' &&
                      (process.env.NEXT_PUBLIC_API_URL || window.location.origin)) ||
                    'https://your-api.com'
                  )
                    .replace(/\/$/, '')}
                  /api/v1/billing/webhooks/stripe
                </code>
              </p>
            </div>
            <div>
              <label className="text-sm font-medium">Success URL (after payment)</label>
              <Input
                placeholder="https://yourapp.com/dashboard/billing?success=1"
                value={form.stripe_success_url}
                onChange={(e) => setForm((f) => ({ ...f, stripe_success_url: e.target.value }))}
                className="mt-1"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Cancel URL (when user cancels)</label>
              <Input
                placeholder="https://yourapp.com/dashboard/billing?canceled=1"
                value={form.stripe_cancel_url}
                onChange={(e) => setForm((f) => ({ ...f, stripe_cancel_url: e.target.value }))}
                className="mt-1"
              />
            </div>
            <div className="flex items-center gap-2">
              <Switch
                checked={form.feature_billing}
                onCheckedChange={(v) => setForm((f) => ({ ...f, feature_billing: v }))}
              />
              <label className="text-sm font-medium">Enable billing (subscriptions & purchases)</label>
            </div>
            <hr className="my-6" />
            <h3 className="font-semibold flex items-center gap-2">
              <Wallet className="h-5 w-5" />
              PayPal
            </h3>
            <p className="text-sm text-muted-foreground">
              Add PayPal as an alternative payment option. Get credentials from the{' '}
              <a
                href="https://developer.paypal.com/dashboard/applications/sandbox"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline inline-flex items-center gap-1"
              >
                PayPal Developer Dashboard
                <ExternalLink className="h-3 w-3" />
              </a>
              . Leave fields blank to keep existing values.
            </p>
            <div>
              <label className="text-sm font-medium">Client ID</label>
              <Input
                type="password"
                placeholder="PayPal client ID"
                value={form.paypal_client_id}
                onChange={(e) => setForm((f) => ({ ...f, paypal_client_id: e.target.value }))}
                className="mt-1 font-mono"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Client secret</label>
              <Input
                type="password"
                placeholder="PayPal client secret"
                value={form.paypal_client_secret}
                onChange={(e) => setForm((f) => ({ ...f, paypal_client_secret: e.target.value }))}
                className="mt-1 font-mono"
                autoComplete="off"
              />
            </div>
            <div>
              <label className="text-sm font-medium">Mode</label>
              <select
                value={form.paypal_mode}
                onChange={(e) => setForm((f) => ({ ...f, paypal_mode: e.target.value }))}
                className="mt-1 flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
              >
                <option value="sandbox">Sandbox (testing)</option>
                <option value="live">Live</option>
              </select>
            </div>
            <Button type="submit" disabled={saving}>
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Save payment settings'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            After saving, restart the API server for changes to take effect. Configure Stripe Price
            IDs on plans (Admin → Template packs) and subscription plans to start receiving
            payments. PayPal checkout integration can be added to the billing flow when configured.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
