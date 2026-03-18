'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

const ONBOARDING_PREF_KEY = 'authora_onboarding_progress_v2';

export default function RestartOnboardingPage() {
  const router = useRouter();

  useEffect(() => {
    const reset = async () => {
      if (typeof window !== 'undefined') {
        const token = localStorage.getItem('access_token');
        if (!token) {
          router.replace('/login?next=/onboarding/restart');
          return;
        }
        localStorage.removeItem(ONBOARDING_PREF_KEY);
      }
      try {
        await api('/api/v1/auth/me/preferences', {
          method: 'PATCH',
          body: JSON.stringify({
            preferences: {
              onboarding_completed: false,
              onboarding_progress: null,
            },
          }),
        });
      } catch {
        // Still redirect - localStorage clear is the main one
      }
      router.replace('/onboarding');
    };
    reset();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-muted/20 to-background p-4">
      <div className="text-center">
        <p className="text-muted-foreground">Restarting onboarding...</p>
      </div>
    </div>
  );
}
