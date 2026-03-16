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
  AlertTriangle,
  MessageSquare,
  Target,
  LifeBuoy,
} from 'lucide-react';

export default function AdminOverviewPage() {
  const [stats, setStats] = useState<{
    users?: number;
    health?: { status: string; checks: Record<string, boolean> };
    alerts?: { failed_export_jobs: number; failed_notification_deliveries: number; has_alerts: boolean };
  } | null>(null);

  useEffect(() => {
    Promise.all([
      api<{ total: number }>('/api/v1/admin/users?limit=1').catch(() => ({ total: 0 })),
      api<{ status: string; checks: Record<string, boolean> }>('/api/v1/admin/health/detailed').catch(() => null),
      api<{ failed_export_jobs: number; failed_notification_deliveries: number; has_alerts: boolean }>(
        '/api/v1/admin/alerts'
      ).catch(() => ({ failed_export_jobs: 0, failed_notification_deliveries: 0, has_alerts: false })),
    ]).then(([usersRes, healthRes, alertsRes]) => {
      setStats({
        users: usersRes?.total ?? 0,
        health: healthRes ?? undefined,
        alerts: alertsRes,
      });
    });
  }, []);

  const links = [
    { href: '/dashboard/admin/users', label: 'User management', icon: Users },
    { href: '/dashboard/admin/feature-flags', label: 'Feature flags', icon: Flag },
    { href: '/dashboard/admin/ai', label: 'AI providers', icon: Zap },
    { href: '/dashboard/admin/ai-usage', label: 'AI usage', icon: Zap },
    { href: '/dashboard/admin/export-jobs', label: 'Export jobs', icon: FileDown },
    { href: '/dashboard/admin/notification-logs', label: 'Notification logs', icon: MessageSquare },
    { href: '/dashboard/admin/reminders', label: 'Reminders', icon: Bell },
    { href: '/dashboard/admin/health', label: 'System health', icon: Activity },
    { href: '/dashboard/admin/setup', label: 'Setup state', icon: Database },
    { href: '/dashboard/admin/storage', label: 'Storage', icon: HardDrive },
    { href: '/dashboard/admin/audit', label: 'Audit logs', icon: ScrollText },
    { href: '/dashboard/admin/support', label: 'Support tools', icon: LifeBuoy },
    { href: '/dashboard/admin/accountability-rules', label: 'Accountability rules', icon: Target },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Operator dashboard</h1>
        <p className="text-muted-foreground mt-1">
          User management, feature flags, monitoring, and system controls.
        </p>
      </div>

      {stats?.alerts?.has_alerts && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4 flex items-center gap-4">
          <AlertTriangle className="h-5 w-5 text-destructive shrink-0" />
          <div className="flex-1">
            <p className="font-medium">Operational alerts</p>
            <p className="text-sm text-muted-foreground">
              {stats.alerts.failed_export_jobs} failed export jobs · {stats.alerts.failed_notification_deliveries}{' '}
              failed notification deliveries
            </p>
          </div>
          <Link
            href="/dashboard/admin/export-jobs?status=failed"
            className="text-sm font-medium text-primary hover:underline"
          >
            View failed jobs
          </Link>
          <Link
            href="/dashboard/admin/notification-logs?status=failed"
            className="text-sm font-medium text-primary hover:underline"
          >
            View failed notifications
          </Link>
        </div>
      )}

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
