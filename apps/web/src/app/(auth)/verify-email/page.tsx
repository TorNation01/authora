'use client';

import { Suspense, useEffect, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';

function VerifyEmailInner() {
  const params = useSearchParams();
  const token = params.get('token') || '';
  const [state, setState] = useState<'working' | 'done' | 'error'>('working');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function run() {
      if (!token) {
        setState('error');
        setMessage('This link is missing its token. Open the link from your inbox again.');
        return;
      }
      try {
        const res = await api<{ verified: boolean; email?: string }>('/api/v1/auth/verify-email', {
          method: 'POST',
          body: JSON.stringify({ token }),
        });
        if (cancelled) return;
        setEmail(res.email || '');
        setState('done');
      } catch (err) {
        if (cancelled) return;
        setState('error');
        setMessage(
          err instanceof Error && err.message
            ? err.message
            : 'That link is invalid or has expired. Sign in and request a new one.'
        );
      }
    }

    run();
    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <CardTitle>
          {state === 'done' ? 'Email confirmed' : state === 'error' ? 'That link did not work' : 'Confirming your email'}
        </CardTitle>
        <CardDescription>
          {state === 'working' && 'One moment.'}
          {state === 'done' && (email ? `${email} is confirmed.` : 'Your address is confirmed.')}
          {state === 'error' && 'Nothing has changed on your account.'}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {state === 'done' && (
          <>
            <p className="text-sm text-muted-foreground">
              Your trial keeps running and checkout is now open. Nothing else to do.
            </p>
            <Button asChild className="w-full">
              <Link href="/dashboard">Go to my library</Link>
            </Button>
          </>
        )}

        {state === 'error' && (
          <>
            <p className="text-sm text-muted-foreground">{message}</p>
            <Button asChild className="w-full">
              <Link href="/login">Sign in and resend</Link>
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={null}>
      <VerifyEmailInner />
    </Suspense>
  );
}
