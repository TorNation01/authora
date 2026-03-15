'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useConfig } from '@/contexts/ConfigProvider';
import { Button } from '@/components/ui/button';

/**
 * SSO entry point for Anakatech mode.
 * When sso_ready is false: redirect to login.
 * When sso_ready is true but SSO not configured: show message and link to login.
 */
export default function SSOPage() {
  const config = useConfig();

  useEffect(() => {
    if (!config.feature_flags.sso_ready) {
      window.location.href = '/login';
      return;
    }
  }, [config.feature_flags.sso_ready]);

  if (!config.feature_flags.sso_ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Redirecting to sign in...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="max-w-md text-center space-y-4">
        <h1 className="font-serif text-2xl font-semibold">SSO Sign In</h1>
        <p className="text-muted-foreground">
          Single sign-on is not yet configured for this deployment. Use local login instead.
        </p>
        <Button asChild>
          <Link href="/login">Go to login</Link>
        </Button>
      </div>
    </div>
  );
}
