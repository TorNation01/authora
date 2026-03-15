'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api } from '@/lib/api';

export default function AdminNotificationLogsPage() {
  const searchParams = useSearchParams();
  const [statusFilter, setStatusFilter] = useState<string>(
    () => searchParams.get('status') || ''
  );
  const [data, setData] = useState<{
    logs: Array<{
      id: string;
      user_id: string;
      notification_type: string;
      channel: string;
      status: string;
      error_message: string | null;
      retry_count: number;
      created_at: string | null;
      sent_at: string | null;
    }>;
  } | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (statusFilter) params.set('status_filter', statusFilter);
    api<typeof data>(`/api/v1/admin/notification-logs?${params}`)
      .then(setData)
      .catch(() => setData(null));
  }, [statusFilter]);

  const failedCount = data?.logs?.filter((l) => l.status === 'failed').length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Notification delivery logs</h1>
        <p className="text-muted-foreground mt-1">
          Track in-app and email notification delivery status.
        </p>
      </div>

      {failedCount > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 dark:border-amber-900 dark:bg-amber-950/30 p-4">
          <p className="text-sm font-medium text-amber-800 dark:text-amber-200">
            {failedCount} failed delivery{failedCount !== 1 ? 's' : ''}
          </p>
          <p className="text-xs text-amber-700 dark:text-amber-300 mt-1">
            Check error messages below. Email delivery may require SMTP/SendGrid configuration.
          </p>
        </div>
      )}

      <Card variant="soft">
        <CardHeader className="flex flex-row items-center justify-between">
          <h2 className="font-semibold">Delivery history</h2>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All statuses</SelectItem>
              <SelectItem value="sent">Sent</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent>
          {data?.logs?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">Type</th>
                    <th className="text-left p-3">Channel</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">User</th>
                    <th className="text-left p-3">Created</th>
                    <th className="text-left p-3">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {data.logs.map((l) => (
                    <tr key={l.id} className="border-t">
                      <td className="p-3">{l.notification_type}</td>
                      <td className="p-3">{l.channel}</td>
                      <td className="p-3">
                        <span
                          className={
                            l.status === 'failed'
                              ? 'text-destructive'
                              : l.status === 'sent'
                                ? 'text-green-600'
                                : 'text-muted-foreground'
                          }
                        >
                          {l.status}
                        </span>
                      </td>
                      <td className="p-3 font-mono text-xs">{l.user_id.slice(0, 8)}…</td>
                      <td className="p-3">{l.created_at ?? '—'}</td>
                      <td className="p-3 text-muted-foreground max-w-[200px] truncate">
                        {l.error_message ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No notification logs.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
