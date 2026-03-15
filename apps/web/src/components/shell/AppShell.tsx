'use client';

import { usePathname } from 'next/navigation';
import { BrandedSidebar } from '@/components/layout/BrandedSidebar';
import { useConfig } from '@/contexts/ConfigProvider';

interface AppShellProps {
  children: React.ReactNode;
  onLogout: () => void;
}

/**
 * Conditional app shell - full sidebar in standalone, embeddable (no shell) in Anakatech.
 */
export function AppShell({ children, onLogout }: AppShellProps) {
  const config = useConfig();

  if (config.feature_flags.embeddable_shell && config.is_anakatech) {
    return <div className="min-h-screen">{children}</div>;
  }

  return (
    <div className="min-h-screen flex">
      <BrandedSidebar onLogout={onLogout} />
      <main className="flex-1 overflow-auto bg-background">{children}</main>
    </div>
  );
}
