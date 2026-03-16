'use client';

import Link from 'next/link';
import { useHelp } from '@/contexts/HelpContext';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  LogOut,
  Settings,
  Target,
  Trophy,
  FileText,
  Map,
  StickyNote,
  HelpCircle,
  Shield,
} from 'lucide-react';
import { NotificationBell } from '@/components/notifications/NotificationBell';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { useUser } from '@/contexts/UserContext';

interface NavItem {
  href: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const mainNav: NavItem[] = [
  { href: '/dashboard', label: 'Home', icon: LayoutDashboard },
  { href: '/dashboard/notes', label: 'Ideas & notes', icon: StickyNote },
  { href: '/dashboard/journey', label: 'Your journey', icon: Map },
  { href: '/dashboard/accountability', label: 'Progress', icon: Target },
  { href: '/dashboard/gamification', label: 'Celebrations', icon: Trophy },
  { href: '/dashboard/export', label: 'Export', icon: FileText },
  { href: '/dashboard/settings', label: 'Settings', icon: Settings },
];

export function BrandedSidebar({
  onLogout,
  children,
  onNavigate,
  className,
}: {
  onLogout: () => void;
  children?: React.ReactNode;
  onNavigate?: () => void;
  className?: string;
}) {
  const pathname = usePathname();
  const { branding } = useConfig();
  const { openHelpCenter } = useHelp();
  const user = useUser();

  const navItems = [
    ...mainNav,
    ...(user?.is_admin ? [{ href: '/dashboard/admin', label: 'Admin', icon: Shield }] : []),
  ];

  return (
    <aside className={cn('flex w-56 flex-col border-r border-border/60 bg-card/50', className)}>
      <div className="flex h-14 items-center border-b border-border/60 px-4">
        <Link href="/dashboard" className="flex items-center gap-2">
          {branding.logo_url ? (
            <img src={branding.logo_url} alt="" width={28} height={28} className="rounded object-contain" />
          ) : null}
          <span className="text-xl font-serif font-bold text-foreground">
            {branding.product_name}
          </span>
        </Link>
        <NotificationBell />
      </div>
      <nav className="flex-1 space-y-0.5 p-3">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                'flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary/10 text-primary'
                  : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      {children}
      <div className="border-t border-border/60 p-3 space-y-1">
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={() => openHelpCenter()}
        >
          <HelpCircle className="h-4 w-4 mr-2" />
          Help
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="w-full justify-start text-muted-foreground hover:text-foreground"
          onClick={onLogout}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Sign out
        </Button>
      </div>
    </aside>
  );
}
