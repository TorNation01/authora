'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { Bell, Check, Mail, AlertCircle, ArrowLeft } from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';

interface Notification {
  id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}

interface DeliveryLog {
  id: string;
  notification_type: string;
  channel: string;
  status: string;
  error_message: string | null;
  retry_count: number;
  created_at: string;
  sent_at: string | null;
}

const TYPE_LABELS: Record<string, string> = {
  daily_reminder: 'Daily goal',
  weekly_reminder: 'Weekly check-in',
  milestone_reminder: 'Milestone',
  streak_reminder: 'Streak',
  overdue_nudge: 'Catch-up',
  finish_date_risk: 'Finish date',
  resume_reminder: 'Resume writing',
  section_reminder: 'You were working on this',
  chapter_target_reminder: 'Chapter target',
  stuck_nudge: 'Ready when you are',
  missed_goal_recovery: 'Recovery plan',
  test_notification: 'Test',
};

function formatDate(s: string): string {
  return new Date(s).toLocaleString();
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [logs, setLogs] = useState<DeliveryLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'notifications' | 'logs'>('notifications');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [n, l] = await Promise.all([
        api<Notification[]>('/api/v1/accountability/notifications?limit=100'),
        api<DeliveryLog[]>('/api/v1/accountability/delivery-logs?limit=100'),
      ]);
      setNotifications(n);
      setLogs(l);
    } catch {
      setNotifications([]);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const markRead = useCallback(
    async (id: string) => {
      try {
        await api(`/api/v1/accountability/notifications/${id}/read`, {
          method: 'POST',
        });
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === id ? { ...n, read_at: new Date().toISOString() } : n
          )
        );
      } catch {
        /* ignore */
      }
    },
    []
  );

  const markAllRead = useCallback(async () => {
    const unread = notifications.filter((n) => !n.read_at);
    for (const n of unread) {
      try {
        await api(`/api/v1/accountability/notifications/${n.id}/read`, {
          method: 'POST',
        });
      } catch {
        /* skip */
      }
    }
    setNotifications((prev) =>
      prev.map((n) => ({ ...n, read_at: n.read_at ?? new Date().toISOString() }))
    );
  }, [notifications]);

  const unreadCount = notifications.filter((n) => !n.read_at).length;

  return (
    <div className="p-6 lg:p-8 max-w-4xl space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/dashboard/accountability"
          className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Progress
        </Link>
      </div>

      <PageHeader
        title="Notification Center"
        description="In-app notifications and delivery history. Configure reminders in Progress settings."
      />

      <div className="flex gap-2 border-b">
        <button
          type="button"
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
            activeTab === 'notifications'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
          onClick={() => setActiveTab('notifications')}
        >
          Notifications ({notifications.length})
        </button>
        <button
          type="button"
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 -mb-px transition-colors',
            activeTab === 'logs'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
          onClick={() => setActiveTab('logs')}
        >
          Delivery logs
        </button>
      </div>

      {activeTab === 'notifications' && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                In-app notifications
              </CardTitle>
              <CardDescription>
                Reminders and updates. Your work is never lost—we keep you on track.
              </CardDescription>
            </div>
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={markAllRead}>
                Mark all read
              </Button>
            )}
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : notifications.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No notifications yet. Enable reminders in Progress settings to receive supportive
                nudges.
              </p>
            ) : (
              <div className="space-y-2">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    className={cn(
                      'rounded-lg border p-4 cursor-pointer transition-colors hover:bg-muted/50',
                      !n.read_at && 'bg-primary/5 border-primary/20'
                    )}
                    onClick={() => !n.read_at && markRead(n.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{n.title}</p>
                          {!n.read_at && (
                            <span className="shrink-0 rounded-full bg-primary/20 px-2 py-0.5 text-xs">
                              New
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mt-0.5 line-clamp-2">
                          {n.body}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2">
                          {TYPE_LABELS[n.type] ?? n.type} · {formatDate(n.created_at)}
                        </p>
                      </div>
                      {!n.read_at && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            markRead(n.id);
                          }}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {activeTab === 'logs' && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              Delivery logs
            </CardTitle>
            <CardDescription>
              Track in-app and email delivery. Failed emails are retried automatically.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-sm text-muted-foreground">Loading...</p>
            ) : logs.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No delivery logs yet. Logs appear when reminders are sent.
              </p>
            ) : (
              <div className="space-y-2">
                {logs.map((l) => (
                  <div
                    key={l.id}
                    className="flex items-center justify-between rounded-lg border p-3 text-sm"
                  >
                    <div>
                      <p className="font-medium">
                        {TYPE_LABELS[l.notification_type] ?? l.notification_type}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {l.channel} · {formatDate(l.created_at)}
                        {l.sent_at && ` · Sent ${formatDate(l.sent_at)}`}
                      </p>
                      {l.error_message && (
                        <p className="text-xs text-destructive mt-1 flex items-center gap-1">
                          <AlertCircle className="h-3 w-3" />
                          {l.error_message}
                          {l.retry_count > 0 && ` (retry ${l.retry_count})`}
                        </p>
                      )}
                    </div>
                    <span
                      className={cn(
                        'rounded px-2 py-0.5 text-xs font-medium',
                        l.status === 'sent'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : l.status === 'failed'
                            ? 'bg-destructive/10 text-destructive'
                            : 'bg-muted text-muted-foreground'
                      )}
                    >
                      {l.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card variant="soft">
        <CardContent className="pt-6">
          <p className="text-sm text-muted-foreground">
            Reminders are supportive, never spammy. Configure times, quiet hours, and which reminders
            you want in{' '}
            <Link href="/dashboard/accountability" className="text-primary hover:underline">
              Progress settings
            </Link>
            . Email reminders require email to be configured by your administrator.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
