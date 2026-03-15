'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { Bell } from 'lucide-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Notification {
  id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}

export function NotificationBell() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const list = await api<Notification[]>(
        '/api/v1/accountability/notifications?limit=10&unread_only=false'
      );
      setNotifications(list);
    } catch {
      setNotifications([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) load();
  }, [open, load]);

  const unreadCount = notifications.filter((n) => !n.read_at).length;

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

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="relative"
        onClick={() => setOpen((o) => !o)}
      >
        <Bell className="h-4 w-4" />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[10px] font-medium text-primary-foreground">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </Button>
      {open && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setOpen(false)}
            aria-hidden
          />
          <div className="absolute right-0 top-full z-20 mt-1 w-80 rounded-lg border bg-popover shadow-lg">
            <div className="border-b px-4 py-2">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold">Notifications</h3>
                <div className="flex gap-2">
                  <Link
                    href="/dashboard/notifications"
                    className="text-xs text-primary hover:underline"
                    onClick={() => setOpen(false)}
                  >
                    View all
                  </Link>
                  <Link
                    href="/dashboard/accountability"
                    className="text-xs text-muted-foreground hover:text-foreground"
                    onClick={() => setOpen(false)}
                  >
                    Settings
                  </Link>
                </div>
              </div>
            </div>
            <div className="max-h-64 overflow-auto">
              {loading ? (
                <p className="p-4 text-sm text-muted-foreground">Loading...</p>
              ) : notifications.length === 0 ? (
                <p className="p-4 text-sm text-muted-foreground">
                  No notifications yet.
                </p>
              ) : (
                notifications.map((n) => (
                  <div
                    key={n.id}
                    className={cn(
                      'border-b px-4 py-3 last:border-0 cursor-pointer hover:bg-muted/50',
                      !n.read_at && 'bg-primary/5'
                    )}
                    onClick={() => {
                      if (!n.read_at) markRead(n.id);
                    }}
                  >
                    <p className="font-medium text-sm">{n.title}</p>
                    <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                      {n.body}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(n.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
