'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { AppShell } from '@/components/shell/AppShell';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { getToken, getRefreshToken, clearTokens } from '@/lib/auth';
import { useConfig } from '@/contexts/ConfigProvider';
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
      .then((data) => setUser({
        id: data.id,
        email: data.email,
        display_name: data.display_name,
        is_admin: data.is_admin ?? false,
      }))
      .catch(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        router.replace('/login');
      })
      .finally(() => setReady(true));
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
    router.push(config.feature_flags.standalone_landing ? '/' : '/sso');
    router.refresh();
  }

  if (!ready) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading your writing space...</p>
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
