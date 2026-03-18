'use client';

import { useState, useEffect } from 'react';
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

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const config = useConfig();
  const nextUrl = searchParams.get('next');

  useEffect(() => {
    if (config?.feature_flags?.sso_ready && !config?.feature_flags?.standalone_auth) {
      router.replace('/sso');
    }
  }, [config?.feature_flags?.sso_ready, config?.feature_flags?.standalone_auth, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api<{ access_token: string; refresh_token: string }>(
        '/api/v1/auth/login',
        {
          method: 'POST',
          body: JSON.stringify({ email, password }),
        }
      );
      setTokens(res.access_token, res.refresh_token);
      toast({ title: 'Welcome back!', description: 'Redirecting...' });
      if (nextUrl && nextUrl.startsWith('/')) {
        router.push(nextUrl);
      } else {
        try {
          const prefs = await api<{ preferences?: { onboarding_completed?: boolean } }>('/api/v1/auth/me/preferences');
          if (prefs?.preferences?.onboarding_completed !== true) {
            router.push('/onboarding');
          } else {
            router.push('/dashboard');
          }
        } catch {
          router.push('/dashboard');
        }
      }
      router.refresh();
    } catch (err) {
      toast({
        title: 'Sign in failed',
        description: err instanceof Error ? err.message : 'Please check your credentials.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-background p-4 sm:p-6 overflow-y-auto">
      <div className="w-full max-w-md my-auto py-6 sm:py-8">
        <Link
          href={getMarketingBaseUrl() || '/'}
          className="mb-6 sm:mb-8 inline-block font-serif text-xl font-bold text-foreground hover:text-primary transition-colors"
        >
          {config?.branding?.product_name ?? 'AUTHORA'}
        </Link>
        <Card variant="sanctuary">
          <CardHeader className="space-y-1 px-4 sm:px-6">
            <CardTitle className="text-2xl font-serif text-foreground">Welcome back</CardTitle>
            <CardDescription className="text-muted-foreground">Sign in to continue your writing journey</CardDescription>
          </CardHeader>
          <CardContent className="px-4 sm:px-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-foreground">Email</Label>
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
                <Label htmlFor="password" className="text-foreground">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
              <Button type="submit" className="w-full h-11" disabled={loading}>
                {loading ? 'Signing in...' : 'Sign in'}
              </Button>
            </form>
            {config?.feature_flags?.standalone_auth && (
              <p className="mt-6 text-center text-sm text-muted-foreground">
                Don&apos;t have an account?{' '}
                <Link href="/register" className="text-primary font-medium hover:underline">
                  Create one
                </Link>
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
