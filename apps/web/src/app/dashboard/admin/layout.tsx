'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useUser } from '@/contexts/UserContext';
import { api } from '@/lib/api';
import {
  Users,
  Flag,
  Zap,
  FileDown,
  Bell,
  AlertTriangle,
  Activity,
  Database,
  HardDrive,
  ScrollText,
  LifeBuoy,
  FileText,
  Upload,
  MessageSquare,
  Trophy,
  Target,
  Gift,
  Ticket,
  Compass,
  DollarSign,
  TrendingUp,
  BookOpen,
  Package,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const adminNav = [
  { href: '/dashboard/admin', label: 'Overview', icon: Activity },
  { href: '/dashboard/admin/users', label: 'Users', icon: Users },
  { href: '/dashboard/admin/feature-flags', label: 'Feature flags', icon: Flag },
  { href: '/dashboard/admin/ai-usage', label: 'AI usage', icon: Zap },
  { href: '/dashboard/admin/export-jobs', label: 'Export jobs', icon: FileDown },
  { href: '/dashboard/admin/notification-logs', label: 'Notification logs', icon: MessageSquare },
  { href: '/dashboard/admin/reminders', label: 'Reminders', icon: Bell },
  { href: '/dashboard/admin/errors', label: 'Error monitoring', icon: AlertTriangle },
  { href: '/dashboard/admin/health', label: 'System health', icon: Database },
  { href: '/dashboard/admin/setup', label: 'Setup state', icon: Database },
  { href: '/dashboard/admin/storage', label: 'Storage', icon: HardDrive },
  { href: '/dashboard/admin/audit', label: 'Audit logs', icon: ScrollText },
  { href: '/dashboard/admin/grants', label: 'Entitlement grants', icon: Gift },
  { href: '/dashboard/admin/promo-codes', label: 'Promo codes', icon: Ticket },
  { href: '/dashboard/admin/entitlement-audit', label: 'Entitlement audit', icon: ScrollText },
  { href: '/dashboard/admin/support', label: 'Support tools', icon: LifeBuoy },
  { href: '/dashboard/admin/content', label: 'Content templates', icon: FileText },
  { href: '/dashboard/admin/onboarding', label: 'Onboarding', icon: Compass },
  { href: '/dashboard/admin/activation', label: 'Activation', icon: TrendingUp },
  { href: '/dashboard/admin/templates', label: 'Templates', icon: BookOpen },
  { href: '/dashboard/admin/template-packs', label: 'Template packs', icon: Package },
  { href: '/dashboard/admin/creators', label: 'Creators', icon: Users },
  { href: '/dashboard/admin/creator-payouts', label: 'Creator payouts', icon: DollarSign },
  { href: '/dashboard/admin/template-submissions', label: 'Template submissions', icon: Upload },
  { href: '/dashboard/admin/encouragement', label: 'Encouragement messages', icon: MessageSquare },
  { href: '/dashboard/admin/accountability-rules', label: 'Accountability rules', icon: Target },
  { href: '/dashboard/admin/gamification', label: 'Gamification', icon: Trophy },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const user = useUser();
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    if (user === null) return;
    if (!user?.is_admin) {
      router.replace('/dashboard');
      return;
    }
    api('/api/v1/admin/users?limit=1')
      .then(() => setVerified(true))
      .catch(() => router.replace('/dashboard'));
  }, [user, router]);

  if (user === null || !user?.is_admin || !verified) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Verifying admin access...</p>
      </div>
    );
  }

  return (
    <div className="flex min-h-[calc(100vh-0px)]">
      <aside className="w-56 border-r bg-card/50 p-4 space-y-1">
        <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground block mb-4">
          ← Dashboard
        </Link>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-2 mb-2">
          Operator
        </p>
        {adminNav.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
              pathname === item.href
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            {item.label}
          </Link>
        ))}
      </aside>
      <main className="flex-1 overflow-auto p-6 lg:p-8">{children}</main>
    </div>
  );
}
