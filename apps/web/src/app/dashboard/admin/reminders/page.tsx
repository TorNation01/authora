'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminRemindersPage() {
  const [data, setData] = useState<{
    reminders: Array<{
      id: string;
      user_id: string;
      reminder_type: string;
      scheduled_time: string;
      is_active: boolean;
      last_triggered_at: string | null;
    }>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/reminders').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Reminders</h1>
        <p className="text-muted-foreground mt-1">Scheduled reminders across users.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data?.reminders?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">User</th>
                    <th className="text-left p-3">Type</th>
                    <th className="text-left p-3">Time</th>
                    <th className="text-left p-3">Active</th>
                    <th className="text-left p-3">Last triggered</th>
                  </tr>
                </thead>
                <tbody>
                  {data.reminders.map((r) => (
                    <tr key={r.id} className="border-t">
                      <td className="p-3 font-mono text-xs">{r.user_id}</td>
                      <td className="p-3">{r.reminder_type}</td>
                      <td className="p-3">{r.scheduled_time}</td>
                      <td className="p-3">{r.is_active ? 'Yes' : 'No'}</td>
                      <td className="p-3">{r.last_triggered_at ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No reminders.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
