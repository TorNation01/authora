'use client';

import { Suspense, useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { setTokens } from '@/lib/auth';
import { useConfig } from '@/contexts/ConfigProvider';
import { getMarketingBaseUrl } from '@/lib/config';

function RegisterForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [inviteCode, setInviteCode] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const referralCode = searchParams?.get('ref') || undefined;
  const { toast } = useToast();
  const config = useConfig();

  // What the server says signup needs right now: an invite code while the beta
  // gate is closed, a Turnstile challenge once bot protection is armed. Asking
  // the API means lifting the gate needs no rebuild of this page.
  const [signup, setSignup] = useState<{
    invite_required: boolean;
    turnstile: { enabled: boolean; site_key: string };
  } | null>(null);
  const [turnstileToken, setTurnstileToken] = useState('');
  const widgetRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let cancelled = false;
    api<{ invite_required: boolean; turnstile: { enabled: boolean; site_key: string } }>(
      '/api/v1/auth/signup-config'
    )
      .then((cfg) => {
        if (!cancelled) setSignup(cfg);
      })
      .catch(() => {
        // Never widen signup because a config read failed: fall back to what
        // the gate has always been.
        if (!cancelled) setSignup({ invite_required: true, turnstile: { enabled: false, site_key: '' } });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const cfg = signup?.turnstile;
    if (!cfg?.enabled || !cfg.site_key) return;

    const renderWidget = () => {
      const turnstile = (window as unknown as {
        turnstile?: {
          render: (el: HTMLElement, opts: Record<string, unknown>) => string;
        };
      }).turnstile;
      if (!turnstile || !widgetRef.current) return;
      widgetRef.current.innerHTML = '';
      turnstile.render(widgetRef.current, {
        sitekey: cfg.site_key,
        callback: (token: string) => setTurnstileToken(token),
        'expired-callback': () => setTurnstileToken(''),
        'error-callback': () => setTurnstileToken(''),
      });
    };

    const existing = document.querySelector<HTMLScriptElement>('script[data-turnstile]');
    if (existing) {
      if ((window as unknown as { turnstile?: unknown }).turnstile) renderWidget();
      else existing.addEventListener('load', renderWidget);
      return () => existing.removeEventListener('load', renderWidget);
    }

    const script = document.createElement('script');
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async = true;
    script.defer = true;
    script.dataset.turnstile = 'true';
    script.addEventListener('load', renderWidget);
    document.head.appendChild(script);
    return () => script.removeEventListener('load', renderWidget);
  }, [signup]);

  useEffect(() => {
    if (!config.feature_flags.standalone_auth) {
      router.replace(config.feature_flags.sso_ready ? '/sso' : '/login');
    }
  }, [config.feature_flags.standalone_auth, config.feature_flags.sso_ready, router]);

  function readVisitorId(): string | undefined {
    if (typeof document === 'undefined') return undefined;
    const match = document.cookie.match(/(?:^|;\s*)av_id=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : undefined;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (signup?.turnstile.enabled && !turnstileToken) {
      toast({
        title: 'One more step',
        description: 'Please complete the bot check below the form.',
        variant: 'destructive',
      });
      return;
    }
    setLoading(true);
    try {
      const res = await api<{ access_token: string; refresh_token: string }>(
        '/api/v1/auth/register',
        {
          method: 'POST',
          body: JSON.stringify({
            email,
            password,
            display_name: displayName || undefined,
            referral_code: referralCode,
            invite_code: inviteCode.trim() || undefined,
            turnstile_token: turnstileToken || undefined,
            // Anonymous visit id from the `av_id` cookie, set by the marketing
            // site's middleware. This is what ties this account back to the
            // page view that produced it on the funnel ladder.
            visitor_id: readVisitorId(),
          }),
        }
      );
      setTokens(res.access_token, res.refresh_token);
      toast({ title: 'Account created!', description: 'Welcome to AUTHORA.' });
      router.push('/onboarding');
      router.refresh();
    } catch (err) {
      // Turnstile tokens are single-use: a retry needs a fresh one, or the
      // second attempt is rejected for a token that already spent itself.
      setTurnstileToken('');
      const turnstile = (window as unknown as {
        turnstile?: { reset: (el?: HTMLElement) => void };
      }).turnstile;
      if (turnstile && widgetRef.current) turnstile.reset(widgetRef.current);
      toast({
        title: 'Registration failed',
        description: err instanceof Error ? err.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md">
        <Link
          href={getMarketingBaseUrl() || '/'}
          className="mb-8 inline-block font-serif text-xl font-bold text-foreground hover:text-primary transition-colors"
        >
          {config.branding.product_name}
        </Link>
        <Card variant="sanctuary">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-serif">Create your account</CardTitle>
            <CardDescription>Start your writing journey in minutes</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="displayName">Display name (optional)</Label>
                <Input
                  id="displayName"
                  placeholder="Your name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Your email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password (min 8 characters)</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  minLength={8}
                  required
                  className="h-11"
                />
              </div>
              {signup?.invite_required && (
                <div className="space-y-2">
                  <Label htmlFor="inviteCode">Invite code</Label>
                  <Input
                    id="inviteCode"
                    placeholder="Required — Authora is invite-only"
                    value={inviteCode}
                    onChange={(e) => setInviteCode(e.target.value)}
                    required
                    className="h-11"
                  />
                </div>
              )}
              {signup?.turnstile.enabled && (
                <div className="space-y-2">
                  <div ref={widgetRef} data-testid="turnstile-widget" />
                  <p className="text-xs text-muted-foreground">
                    Protected by Cloudflare Turnstile.
                  </p>
                </div>
              )}
              <Button
                type="submit"
                className="w-full h-11"
                disabled={loading}
              >
                {loading ? 'Creating account...' : 'Create account'}
              </Button>
            </form>
            <p className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link href="/login" className="text-primary font-medium hover:underline">
                Sign in
              </Link>
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center bg-background" />}>
      <RegisterForm />
    </Suspense>
  );
}
