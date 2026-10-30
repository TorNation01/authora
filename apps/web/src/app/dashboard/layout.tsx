'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/shell/AppShell';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { api, ApiError } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { getToken, getRefreshToken, clearTokens } from '@/lib/auth';
import { useConfig } from '@/contexts/ConfigProvider';
import { getMarketingBaseUrl } from '@/lib/config';
import { UserProvider, type UserInfo } from '@/contexts/UserContext';
import { HelpProvider } from '@/contexts/HelpContext';
import { TutorialProvider } from '@/contexts/TutorialContext';
import { UpgradeTriggerProvider } from '@/contexts/UpgradeTriggerContext';
import { HelpCenter, Walkthrough } from '@/components/help';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { toast } = useToast();
  const config = useConfig();
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<UserInfo | null>(null);
  const [bootError, setBootError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  const loginPath = config.feature_flags.sso_ready ? '/sso' : '/login';

  useEffect(() => {
    let cancelled = false;

    // Only bounce when there is no session at all. An expired access token is
    // recoverable: api() refreshes it from the 7-day refresh token on a 401.
    if (!getToken() && !getRefreshToken()) {
      router.replace(loginPath);
      return;
    }

    setBootError(null);

    api<{ id: string; email: string; display_name: string | null; is_admin: boolean }>('/api/v1/auth/me')
      .then((data) => {
        if (cancelled) return;
        setUser({
          id: String(data?.id ?? ''),
          email: String(data?.email ?? ''),
          display_name: data?.display_name ?? null,
          is_admin: Boolean(data?.is_admin),
        });
        setReady(true);
      })
      .catch((err) => {
        if (cancelled) return;
        if (err instanceof ApiError && err.status === 401) {
          // The refresh token was rejected too — this session really is over.
          clearTokens();
          router.replace('/login');
          return;
        }
        // Server hiccup, offline laptop, API restart: keep the session and offer
        // a retry rather than signing the user out of their own workspace.
        setBootError(
          err instanceof ApiError
            ? `Authora could not load your session (${err.status}). Your session is still saved.`
            : 'Authora cannot reach the server. Your session is still saved.'
        );
      });

    return () => {
      cancelled = true;
    };
  }, [router, loginPath, attempt]);

  // Keep a long-lived tab warm: refresh the access token well before it expires
  // so a mid-session reload never even hits the 401 path.
  useEffect(() => {
    if (!ready) return;
    const id = window.setInterval(() => {
      api('/api/v1/auth/me').catch(() => {
        /* transient — the next user action retries */
      });
    }, 20 * 60 * 1000);
    return () => window.clearInterval(id);
  }, [ready]);

  async function handleLogout() {
    try {
      const refresh = getRefreshToken();
      if (refresh) {
        await api('/api/v1/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refresh }),
        });
      }
    } catch {
      /* ignore */
    }
    clearTokens();
    toast({ title: 'Signed out' });
    const home = config.feature_flags.standalone_landing ? (getMarketingBaseUrl() || '/') : '/sso';
    if (home.startsWith('http')) {
      window.location.href = home;
    } else {
      router.push(home);
      router.refresh();
    }
  }

  if (bootError) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-background px-6 text-center">
        <p className="text-muted-foreground">{bootError}</p>
        <Button
          onClick={() => {
            setReady(false);
            setAttempt((n) => n + 1);
          }}
        >
          Try again
        </Button>
      </div>
    );
  }

  if (!ready || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-muted-foreground">
          {!ready ? 'Loading your writing space...' : 'Redirecting to sign in...'}
        </p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <UserProvider user={user}>
        <UpgradeTriggerProvider>
          <HelpProvider>
            <TutorialProvider>
              <AppShell onLogout={handleLogout}>{children}</AppShell>
              <HelpCenter />
              <Walkthrough />
            </TutorialProvider>
          </HelpProvider>
        </UpgradeTriggerProvider>
      </UserProvider>
    </ErrorBoundary>
  );
}
