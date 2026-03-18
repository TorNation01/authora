'use client';

import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { LayoutDashboard, BookOpen, TrendingUp, DollarSign, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

type CreatorStatus = {
  status: string | null;
  is_creator: boolean;
  applied_at?: string;
  approved_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
};

const creatorNav = [
  { href: '/dashboard/creator', label: 'Overview', icon: LayoutDashboard },
  { href: '/dashboard/creator/templates', label: 'My templates', icon: BookOpen },
  { href: '/dashboard/creator/performance', label: 'Performance', icon: TrendingUp },
  { href: '/dashboard/creator/earnings', label: 'Earnings', icon: DollarSign },
];

export default function CreatorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [status, setStatus] = useState<CreatorStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<CreatorStatus>('/api/v1/creators/status')
      .then(setStatus)
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  const canAccessDashboard = status?.is_creator === true;

  return (
    <div className="flex min-h-[calc(100vh-0px)]">
      <aside className="w-56 border-r bg-card/50 p-4 space-y-1">
        <Link
          href="/dashboard"
          className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-2 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Dashboard
        </Link>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-2 mb-2">
          Creator
        </p>
        {canAccessDashboard ? (
          creatorNav.map((item) => (
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
          ))
        ) : (
          <Link
            href="/dashboard/creator"
            className={cn(
              'flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors',
              pathname === '/dashboard/creator'
                ? 'bg-primary/10 text-primary'
                : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
            )}
          >
            <LayoutDashboard className="h-4 w-4 shrink-0" />
            Overview
          </Link>
        )}
      </aside>
      <main className="flex-1 overflow-auto p-6 lg:p-8">{children}</main>
    </div>
  );
}
