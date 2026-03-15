'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';
import {
  Users,
  Flag,
  Zap,
  FileDown,
  Bell,
  Activity,
  Database,
  HardDrive,
  ScrollText,
  ChevronRight,
} from 'lucide-react';

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<{
    users?: number;
    health?: { status: string; checks: Record<string, boolean> };
  } | null>(null);

  useEffect(() => {
    Promise.all([
      api<{ total: number }>('/api/v1/admin/users?limit=1').catch(() => ({ total: 0 })),
      api<{ status: string; checks: Record<string, boolean> }>('/api/v1/admin/health/detailed').catch(() => null),
    ]).then(([usersRes, healthRes]) => {
      setStats({
        users: usersRes?.total ?? 0,
        health: healthRes ?? undefined,
      });
    });
  }, []);

  const links = [
    { href: '/dashboard/admin/users', label: 'User management', icon: Users },
    { href: '/dashboard/admin/feature-flags', label: 'Feature flags', icon: Flag },
    { href: '/dashboard/admin/ai-usage', label: 'AI usage', icon: Zap },
    { href: '/dashboard/admin/export-jobs', label: 'Export jobs', icon: FileDown },
    { href: '/dashboard/admin/reminders', label: 'Reminders', icon: Bell },
    { href: '/dashboard/admin/health', label: 'System health', icon: Activity },
    { href: '/dashboard/admin/setup', label: 'Setup state', icon: Database },
    { href: '/dashboard/admin/storage', label: 'Storage', icon: HardDrive },
    { href: '/dashboard/admin/audit', label: 'Audit logs', icon: ScrollText },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Operator dashboard</h1>
        <p className="text-muted-foreground mt-1">
          User management, feature flags, monitoring, and system controls.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card variant="soft">
          <CardHeader className="pb-2">
            <p className="text-sm font-medium text-muted-foreground">Users</p>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats?.users ?? '—'}</p>
          </CardContent>
        </Card>
        <Card variant="soft">
          <CardHeader className="pb-2">
            <p className="text-sm font-medium text-muted-foreground">System status</p>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold capitalize">{stats?.health?.status ?? '—'}</p>
            {stats?.health?.checks && (
              <p className="text-xs text-muted-foreground mt-1">
                DB: {stats.health.checks.database ? '✓' : '✗'} · Redis: {stats.health.checks.redis ? '✓' : '✗'}
              </p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Quick links</h2>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2">
            {links.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 rounded-lg border p-3 hover:bg-muted/50 transition-colors"
              >
                <item.icon className="h-4 w-4 text-muted-foreground" />
                <span className="flex-1">{item.label}</span>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
