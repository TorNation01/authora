'use client';

import { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

interface AuditEntry {
  id: string;
  user_id: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: Record<string, unknown> | null;
  performed_by_id: string;
  created_at: string;
}

export default function AdminEntitlementAuditPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [userFilter, setUserFilter] = useState('');
  const [actionFilter, setActionFilter] = useState('');

  const fetchEntries = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({ limit: '100' });
    if (userFilter) params.set('user_id', userFilter);
    if (actionFilter) params.set('action', actionFilter);
    api<AuditEntry[]>(`/api/v1/billing/admin/audit-log?${params}`)
      .then(setEntries)
      .catch(() => setEntries([]))
      .finally(() => setLoading(false));
  }, [userFilter, actionFilter]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Entitlement audit log</h1>
        <p className="mt-1 text-muted-foreground">Track grant and promo code actions.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <div className="flex gap-4">
            <Input
              placeholder="Filter by user ID"
              value={userFilter}
              onChange={(e) => setUserFilter(e.target.value)}
              className="max-w-xs"
            />
            <Input
              placeholder="Filter by action"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="max-w-xs"
            />
            <button
              type="button"
              onClick={fetchEntries}
              className="text-sm text-primary hover:underline"
            >
              Apply
            </button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading...</p>
          ) : entries.length === 0 ? (
            <p className="text-muted-foreground">No entries.</p>
          ) : (
            <div className="space-y-2">
              {entries.map((e) => (
                <div key={e.id} className="rounded-lg border p-3 text-sm">
                  <div className="flex justify-between">
                    <span className="font-medium">{e.action}</span>
                    <span className="text-muted-foreground">{new Date(e.created_at).toLocaleString()}</span>
                  </div>
                  <div className="mt-1 text-muted-foreground">
                    {e.user_id && <span>user: {e.user_id} </span>}
                    {e.entity_type && <span>entity: {e.entity_type} </span>}
                    {e.entity_id && <span>id: {e.entity_id}</span>}
                  </div>
                  {e.details && Object.keys(e.details).length > 0 && (
                    <pre className="mt-2 overflow-x-auto rounded bg-muted/50 p-2 text-xs">
                      {JSON.stringify(e.details, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
