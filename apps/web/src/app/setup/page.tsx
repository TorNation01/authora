'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Check, X, Loader2, ChevronRight, ChevronLeft } from 'lucide-react';
import { useConfig } from '@/contexts/ConfigProvider';
import { useToast } from '@/hooks/use-toast';

const STEPS = [
  { id: 'branding', title: 'Branding', desc: 'App name and tagline' },
  { id: 'domain', title: 'Domain & SSL', desc: 'Domain and security' },
  { id: 'database', title: 'Database', desc: 'PostgreSQL connection' },
  { id: 'redis', title: 'Redis', desc: 'Redis connection' },
  { id: 'storage', title: 'Storage', desc: 'File storage' },
  { id: 'ai', title: 'AI Provider', desc: 'OpenAI or Anthropic' },
  { id: 'email', title: 'Email', desc: 'Optional email provider' },
  { id: 'admin', title: 'Admin Account', desc: 'First admin user' },
  { id: 'preferences', title: 'Preferences', desc: 'Backup, reminders, analytics' },
  { id: 'finalize', title: 'Go Live', desc: 'Apply and complete' },
];

export default function SetupPage() {
  const router = useRouter();
  const config = useConfig();
  const { toast } = useToast();
  const [step, setStep] = useState(0);
  const [status, setStatus] = useState<{ setup_complete: boolean; can_connect: boolean } | null>(null);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);

  const [form, setForm] = useState({
    product_name: 'AUTHORA',
    tagline: 'AI-Powered Book Builder',
    domain: 'localhost',
    use_ssl: false,
    database_url: 'postgresql://authora:authora@localhost:5432/authora',
    redis_url: 'redis://localhost:6379/0',
    storage_provider: 'local' as 'local' | 's3' | 'r2',
    storage_local_path: './storage',
    ai_provider: 'openai' as 'openai' | 'anthropic',
    ai_model: 'gpt-4o-mini',
    openai_api_key: '',
    anthropic_api_key: '',
    email_enabled: false,
    admin_email: '',
    admin_password: '',
    admin_display_name: 'Admin',
    backup_enabled: true,
    backup_retention_days: 7,
    reminder_enabled: true,
    reminder_default_time: '09:00',
    analytics_enabled: false,
    telemetry_enabled: false,
    mode: 'local' as 'local' | 'cloud',
  });

  useEffect(() => {
    if (!config.feature_flags.standalone_setup_wizard) {
      router.replace('/');
      return;
    }
    const base = process.env.NEXT_PUBLIC_API_URL || '';
    fetch(`${base}/api/v1/setup/status`)
      .then((r) => r.json())
      .then(setStatus)
      .catch(() => setStatus({ setup_complete: false, can_connect: false }));
  }, [config.feature_flags.standalone_setup_wizard, router]);

  const handleTestConnections = async () => {
    setTesting('connections');
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || '';
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const res = await fetch(`${base}/api/v1/setup/test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({
          database_url: form.database_url,
          redis_url: form.redis_url,
        }),
      });
      const data = await res.json();
      if (data.database?.valid) toast({ title: 'Database OK' });
      else toast({ title: 'Database failed', description: data.database?.message, variant: 'destructive' });
      if (data.redis?.valid) toast({ title: 'Redis OK' });
      else toast({ title: 'Redis failed', description: data.redis?.message, variant: 'destructive' });
    } catch (e) {
      toast({ title: 'Test failed', variant: 'destructive' });
    } finally {
      setTesting(null);
    }
  };

  const handleApply = async () => {
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || '';
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      await fetch(`${base}/api/v1/setup/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
        body: JSON.stringify({
          branding: { product_name: form.product_name, tagline: form.tagline },
          domain: { domain: form.domain, use_ssl: form.use_ssl },
          database_url: form.database_url,
          redis_url: form.redis_url,
          storage: {
            storage_provider: form.storage_provider,
            storage_local_path: form.storage_local_path,
          },
          ai: {
            ai_provider: form.ai_provider,
            ai_model: form.ai_model,
            openai_api_key: form.openai_api_key || undefined,
            anthropic_api_key: form.anthropic_api_key || undefined,
          },
          preferences: {
            backup_enabled: form.backup_enabled,
            backup_retention_days: form.backup_retention_days,
            reminder_enabled: form.reminder_enabled,
            reminder_default_time: form.reminder_default_time,
            analytics_enabled: form.analytics_enabled,
            telemetry_enabled: form.telemetry_enabled,
          },
          mode: { mode: form.mode },
        }),
      });
      toast({ title: 'Configuration saved' });
    } catch (e) {
      toast({ title: 'Save failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleFinalize = async () => {
    if (!form.admin_email || !form.admin_password) {
      toast({ title: 'Admin email and password required', variant: 'destructive' });
      return;
    }
    setLoading(true);
    try {
      const base = process.env.NEXT_PUBLIC_API_URL || '';
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) };

      // Apply config first so .env is updated before restart
      await fetch(`${base}/api/v1/setup/apply`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          branding: { product_name: form.product_name, tagline: form.tagline },
          domain: { domain: form.domain, use_ssl: form.use_ssl },
          database_url: form.database_url,
          redis_url: form.redis_url,
          storage: {
            storage_provider: form.storage_provider,
            storage_local_path: form.storage_local_path,
          },
          ai: {
            ai_provider: form.ai_provider,
            ai_model: form.ai_model,
            openai_api_key: form.openai_api_key || undefined,
            anthropic_api_key: form.anthropic_api_key || undefined,
          },
          preferences: {
            backup_enabled: form.backup_enabled,
            backup_retention_days: form.backup_retention_days,
            reminder_enabled: form.reminder_enabled,
            reminder_default_time: form.reminder_default_time,
            analytics_enabled: form.analytics_enabled,
            telemetry_enabled: form.telemetry_enabled,
          },
          mode: { mode: form.mode },
        }),
      });

      const res = await fetch(`${base}/api/v1/setup/finalize`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          database_url: form.database_url,
          admin: {
            admin_email: form.admin_email,
            admin_password: form.admin_password,
            admin_display_name: form.admin_display_name,
          },
          ai: {
            ai_provider: form.ai_provider,
            ai_model: form.ai_model,
            openai_api_key: form.openai_api_key || undefined,
            anthropic_api_key: form.anthropic_api_key || undefined,
          },
          run_migrations: true,
          seed_templates: true,
        }),
      });
      const data = await res.json();
      if (res.ok) {
        toast({ title: 'Setup complete!', description: 'You can now sign in.' });
        router.push('/login');
      } else {
        toast({ title: 'Finalize failed', description: data.detail || 'Unknown error', variant: 'destructive' });
      }
    } catch (e) {
      toast({ title: 'Finalize failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  if (!config.feature_flags.standalone_setup_wizard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Redirecting...</p>
      </div>
    );
  }

  if (status?.setup_complete) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card variant="sanctuary" className="max-w-md">
          <CardHeader>
            <CardTitle>Setup complete</CardTitle>
            <CardDescription>Your instance is already configured.</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/login">Sign in</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentStep = STEPS[step];
  const isLast = step === STEPS.length - 1;
  const isFinalize = currentStep?.id === 'finalize';

  return (
    <div className="min-h-screen bg-background p-4 lg:p-8">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/"
          className="mb-8 inline-block font-serif text-xl font-bold text-foreground hover:text-primary transition-colors"
        >
          {config.branding.product_name}
        </Link>

        <div className="mb-8">
          <div className="flex gap-1 mb-2">
            {STEPS.map((s, i) => (
              <div
                key={s.id}
                className={`h-1 flex-1 rounded ${i <= step ? 'bg-primary' : 'bg-muted'}`}
                title={s.title}
              />
            ))}
          </div>
          <h2 className="font-serif text-lg font-semibold">{currentStep?.title}</h2>
          <p className="text-sm text-muted-foreground">{currentStep?.desc}</p>
        </div>

        <Card variant="sanctuary" className="mb-6">
          <CardContent className="pt-6">
            {currentStep?.id === 'branding' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="product_name">Product name</Label>
                  <Input
                    id="product_name"
                    value={form.product_name}
                    onChange={(e) => setForm((f) => ({ ...f, product_name: e.target.value }))}
                    placeholder="AUTHORA"
                  />
                </div>
                <div>
                  <Label htmlFor="tagline">Tagline</Label>
                  <Input
                    id="tagline"
                    value={form.tagline}
                    onChange={(e) => setForm((f) => ({ ...f, tagline: e.target.value }))}
                    placeholder="AI-Powered Book Builder"
                  />
                </div>
              </div>
            )}

            {currentStep?.id === 'domain' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="domain">Domain</Label>
                  <Input
                    id="domain"
                    value={form.domain}
                    onChange={(e) => setForm((f) => ({ ...f, domain: e.target.value }))}
                    placeholder="localhost or your-domain.com"
                  />
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.use_ssl}
                    onChange={(e) => setForm((f) => ({ ...f, use_ssl: e.target.checked }))}
                  />
                  <span className="text-sm">Expect HTTPS (SSL)</span>
                </label>
              </div>
            )}

            {currentStep?.id === 'database' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="database_url">PostgreSQL URL</Label>
                  <Input
                    id="database_url"
                    value={form.database_url}
                    onChange={(e) => setForm((f) => ({ ...f, database_url: e.target.value }))}
                    placeholder="postgresql://user:pass@host:5432/dbname"
                  />
                </div>
                <Button variant="outline" size="sm" onClick={handleTestConnections} disabled={!!testing}>
                  {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  Test connection
                </Button>
              </div>
            )}

            {currentStep?.id === 'redis' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="redis_url">Redis URL</Label>
                  <Input
                    id="redis_url"
                    value={form.redis_url}
                    onChange={(e) => setForm((f) => ({ ...f, redis_url: e.target.value }))}
                    placeholder="redis://localhost:6379/0"
                  />
                </div>
                <Button variant="outline" size="sm" onClick={handleTestConnections} disabled={!!testing}>
                  {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                  Test connection
                </Button>
              </div>
            )}

            {currentStep?.id === 'storage' && (
              <div className="space-y-4">
                <div>
                  <Label>Storage provider</Label>
                  <select
                    value={form.storage_provider}
                    onChange={(e) => setForm((f) => ({ ...f, storage_provider: e.target.value as 'local' | 's3' | 'r2' }))}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1"
                  >
                    <option value="local">Local filesystem</option>
                    <option value="s3">Amazon S3</option>
                    <option value="r2">Cloudflare R2</option>
                  </select>
                </div>
                {form.storage_provider === 'local' && (
                  <div>
                    <Label htmlFor="storage_local_path">Storage path</Label>
                    <Input
                      id="storage_local_path"
                      value={form.storage_local_path}
                      onChange={(e) => setForm((f) => ({ ...f, storage_local_path: e.target.value }))}
                    />
                  </div>
                )}
              </div>
            )}

            {currentStep?.id === 'ai' && (
              <div className="space-y-4">
                <div>
                  <Label>AI provider</Label>
                  <select
                    value={form.ai_provider}
                    onChange={(e) => setForm((f) => ({ ...f, ai_provider: e.target.value as 'openai' | 'anthropic' }))}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="anthropic">Anthropic</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="ai_model">Model</Label>
                  <Input
                    id="ai_model"
                    value={form.ai_model}
                    onChange={(e) => setForm((f) => ({ ...f, ai_model: e.target.value }))}
                    placeholder="gpt-4o-mini"
                  />
                </div>
                <div>
                  <Label htmlFor="openai_api_key">OpenAI API key (optional)</Label>
                  <Input
                    id="openai_api_key"
                    type="password"
                    value={form.openai_api_key}
                    onChange={(e) => setForm((f) => ({ ...f, openai_api_key: e.target.value }))}
                    placeholder="sk-..."
                  />
                </div>
                <div>
                  <Label htmlFor="anthropic_api_key">Anthropic API key (optional)</Label>
                  <Input
                    id="anthropic_api_key"
                    type="password"
                    value={form.anthropic_api_key}
                    onChange={(e) => setForm((f) => ({ ...f, anthropic_api_key: e.target.value }))}
                    placeholder="sk-ant-..."
                  />
                </div>
              </div>
            )}

            {currentStep?.id === 'email' && (
              <div className="space-y-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.email_enabled}
                    onChange={(e) => setForm((f) => ({ ...f, email_enabled: e.target.checked }))}
                  />
                  <span className="text-sm">Enable email (optional)</span>
                </label>
                {form.email_enabled && (
                  <p className="text-sm text-muted-foreground">
                    Configure SMTP in .env after setup: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
                  </p>
                )}
              </div>
            )}

            {currentStep?.id === 'admin' && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="admin_email">Admin email *</Label>
                  <Input
                    id="admin_email"
                    type="email"
                    value={form.admin_email}
                    onChange={(e) => setForm((f) => ({ ...f, admin_email: e.target.value }))}
                    placeholder="admin@example.com"
                  />
                </div>
                <div>
                  <Label htmlFor="admin_password">Admin password * (min 8 chars)</Label>
                  <Input
                    id="admin_password"
                    type="password"
                    value={form.admin_password}
                    onChange={(e) => setForm((f) => ({ ...f, admin_password: e.target.value }))}
                    placeholder="••••••••"
                    minLength={8}
                  />
                </div>
                <div>
                  <Label htmlFor="admin_display_name">Display name</Label>
                  <Input
                    id="admin_display_name"
                    value={form.admin_display_name}
                    onChange={(e) => setForm((f) => ({ ...f, admin_display_name: e.target.value }))}
                    placeholder="Admin"
                  />
                </div>
              </div>
            )}

            {currentStep?.id === 'preferences' && (
              <div className="space-y-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.backup_enabled}
                    onChange={(e) => setForm((f) => ({ ...f, backup_enabled: e.target.checked }))}
                  />
                  <span className="text-sm">Enable backups</span>
                </label>
                <div>
                  <Label htmlFor="backup_retention">Backup retention (days)</Label>
                  <Input
                    id="backup_retention"
                    type="number"
                    min={1}
                    max={90}
                    value={form.backup_retention_days}
                    onChange={(e) => setForm((f) => ({ ...f, backup_retention_days: parseInt(e.target.value) || 7 }))}
                  />
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.reminder_enabled}
                    onChange={(e) => setForm((f) => ({ ...f, reminder_enabled: e.target.checked }))}
                  />
                  <span className="text-sm">Enable writing reminders</span>
                </label>
                <div>
                  <Label htmlFor="reminder_time">Default reminder time</Label>
                  <Input
                    id="reminder_time"
                    type="time"
                    value={form.reminder_default_time}
                    onChange={(e) => setForm((f) => ({ ...f, reminder_default_time: e.target.value }))}
                  />
                </div>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.analytics_enabled}
                    onChange={(e) => setForm((f) => ({ ...f, analytics_enabled: e.target.checked }))}
                  />
                  <span className="text-sm">Analytics (optional)</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={form.telemetry_enabled}
                    onChange={(e) => setForm((f) => ({ ...f, telemetry_enabled: e.target.checked }))}
                  />
                  <span className="text-sm">Telemetry (optional)</span>
                </label>
                <div>
                  <Label>Mode</Label>
                  <select
                    value={form.mode}
                    onChange={(e) => setForm((f) => ({ ...f, mode: e.target.value as 'local' | 'cloud' }))}
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1"
                  >
                    <option value="local">Local</option>
                    <option value="cloud">Cloud</option>
                  </select>
                </div>
              </div>
            )}

            {currentStep?.id === 'finalize' && (
              <div className="space-y-4">
                <div className="rounded-lg bg-muted/50 p-4 text-sm space-y-2">
                  <p className="font-medium">Go-live checklist</p>
                  <ul className="list-disc list-inside space-y-1 text-muted-foreground">
                    <li>Database and Redis configured</li>
                    <li>Admin account created</li>
                    <li>Migrations applied</li>
                    <li>Starter templates seeded</li>
                    <li>Configuration written to .env</li>
                  </ul>
                </div>
                <p className="text-sm text-muted-foreground">
                  Click &quot;Apply config&quot; to save settings, then &quot;Complete setup&quot; to run migrations and create your admin account.
                </p>
                <div className="flex gap-2">
                  <Button variant="outline" onClick={handleApply} disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                    Apply config
                  </Button>
                  <Button onClick={handleFinalize} disabled={loading}>
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                    Complete setup
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setStep((s) => Math.max(0, s - 1))}
            disabled={step === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            Back
          </Button>
          {!isFinalize && (
            <Button onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))}>
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
