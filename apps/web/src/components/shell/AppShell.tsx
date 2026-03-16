'use client';

import { useState } from 'react';
import { Menu } from 'lucide-react';
import { BrandedSidebar } from '@/components/layout/BrandedSidebar';
import { useConfig } from '@/contexts/ConfigProvider';
import { Sheet, SheetContent } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';

interface AppShellProps {
  children: React.ReactNode;
  onLogout: () => void;
}

/**
 * Conditional app shell - full sidebar in standalone, embeddable (no shell) in Anakatech.
 * Responsive: sidebar as drawer on mobile/tablet, fixed on desktop.
 */
export function AppShell({ children, onLogout }: AppShellProps) {
  const config = useConfig();
  const [mobileOpen, setMobileOpen] = useState(false);

  const useEmbeddable =
    config.feature_flags.embeddable_shell &&
    (config.is_anakatech || config.is_white_label) &&
    (config.integration_flags?.enable_shared_nav !== false);
  if (useEmbeddable) {
    return <div className="min-h-screen">{children}</div>;
  }

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Mobile header */}
      <header className="lg:hidden flex h-14 shrink-0 items-center gap-2 border-b border-border/60 bg-card/50 px-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setMobileOpen(true)}
          aria-label="Open menu"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <span className="font-serif font-bold text-foreground">{config.branding.product_name}</span>
      </header>
      {/* Mobile sidebar drawer */}
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent side="left" className="w-64 p-0">
          <BrandedSidebar onLogout={onLogout} onNavigate={() => setMobileOpen(false)} />
        </SheetContent>
      </Sheet>
      {/* Desktop sidebar */}
      <div className="hidden lg:flex shrink-0">
        <BrandedSidebar onLogout={onLogout} />
      </div>
      <main className="flex-1 min-w-0 overflow-auto bg-background">{children}</main>
    </div>
  );
}
