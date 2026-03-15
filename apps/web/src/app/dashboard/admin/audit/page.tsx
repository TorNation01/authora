'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminAuditPage() {
  const [data, setData] = useState<{
    logs: Array<{
      id: string;
      user_id: string | null;
      action: string;
      resource: string;
      resource_id: string | null;
      ip_address: string | null;
      created_at: string | null;
    }>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/audit-logs').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Audit logs</h1>
        <p className="text-muted-foreground mt-1">Security and compliance audit trail.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data?.logs?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">Action</th>
                    <th className="text-left p-3">Resource</th>
                    <th className="text-left p-3">User</th>
                    <th className="text-left p-3">IP</th>
                    <th className="text-left p-3">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {data.logs.map((l) => (
                    <tr key={l.id} className="border-t">
                      <td className="p-3">{l.action}</td>
                      <td className="p-3">{l.resource}{l.resource_id ? `:${l.resource_id}` : ''}</td>
                      <td className="p-3 font-mono text-xs">{l.user_id ?? '—'}</td>
                      <td className="p-3">{l.ip_address ?? '—'}</td>
                      <td className="p-3">{l.created_at ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No audit logs. AuditLogger may not be used by all endpoints.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
