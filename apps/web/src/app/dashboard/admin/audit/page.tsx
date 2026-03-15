'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

export default function AdminAuditPage() {
  const [userFilter, setUserFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');
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
    const params = new URLSearchParams();
    if (userFilter.trim()) params.set('user_id', userFilter.trim());
    if (resourceFilter.trim()) params.set('resource', resourceFilter.trim());
    if (actionFilter.trim()) params.set('action', actionFilter.trim());
    api<typeof data>(`/api/v1/admin/audit-logs?${params}`).then(setData).catch(() => setData(null));
  }, [userFilter, resourceFilter, actionFilter]);

  const clearFilters = () => {
    setUserFilter('');
    setResourceFilter('');
    setActionFilter('');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Audit logs</h1>
        <p className="text-muted-foreground mt-1">Security and compliance audit trail.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6 space-y-4">
          <div className="flex flex-wrap gap-2 items-center">
            <Input
              placeholder="User ID"
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
              className="max-w-[200px]"
            />
            <Input
              placeholder="Resource"
              value={resourceFilter}
              onChange={(e) => setResourceFilter(e.target.value)}
              className="max-w-[140px]"
            />
            <Input
              placeholder="Action"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="max-w-[140px]"
            />
            <Button variant="outline" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          </div>
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
