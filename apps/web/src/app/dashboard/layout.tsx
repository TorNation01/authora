'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/shell/AppShell';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { getToken, getRefreshToken, clearTokens } from '@/lib/auth';
import { useConfig } from '@/contexts/ConfigProvider';
import { getMarketingBaseUrl } from '@/lib/config';
import { UserProvider, type UserInfo } from '@/contexts/UserContext';
import { HelpProvider } from '@/contexts/HelpContext';
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

  const loginPath = config.feature_flags.sso_ready ? '/sso' : '/login';

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.replace(loginPath);
      return;
    }
    api<{ id: string; email: string; display_name: string | null; is_admin: boolean }>('/api/v1/auth/me')
      .then((data) => {
        setUser({
          id: String(data?.id ?? ''),
          email: String(data?.email ?? ''),
          display_name: data?.display_name ?? null,
          is_admin: Boolean(data?.is_admin),
        });
        setReady(true);
      })
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.replace('/login');
        // Do not setReady - stay in loading state until redirect
      });
  }, [router, loginPath]);

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
        <HelpProvider>
          <AppShell onLogout={handleLogout}>{children}</AppShell>
          <HelpCenter />
          <Walkthrough />
        </HelpProvider>
      </UserProvider>
    </ErrorBoundary>
  );
}
