'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminHealthPage() {
  const [health, setHealth] = useState<{
    status: string;
    checks: Record<string, unknown>;
    config?: Record<string, string | boolean>;
  } | null>(null);

  useEffect(() => {
    api<typeof health>('/api/v1/admin/health/detailed').then(setHealth).catch(() => setHealth(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">System health</h1>
        <p className="text-muted-foreground mt-1">Database, Redis, and config status.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Status</h2>
        </CardHeader>
        <CardContent>
          {health ? (
            <div className="space-y-2">
              <p className="text-lg font-medium capitalize">{health.status}</p>
              <div className="grid gap-2 sm:grid-cols-2">
                {Object.entries(health.checks).map(([k, v]) => (
                  <div key={k} className="rounded border p-3">
                    <p className="text-sm font-medium">{k}</p>
                    <p className={v === true ? 'text-green-600' : 'text-muted-foreground'}>
                      {typeof v === 'boolean' ? (v ? 'OK' : 'Failed') : String(v)}
                    </p>
                  </div>
                ))}
              </div>
              {health.config && (
                <div className="mt-4">
                  <p className="text-sm font-medium mb-2">Config indicators</p>
                  <div className="grid gap-2 sm:grid-cols-2">
                    {Object.entries(health.config).map(([k, v]) => (
                      <div key={k} className="rounded border p-3">
                        <p className="text-sm font-medium">{k.replace(/_/g, ' ')}</p>
                        <p
                          className={
                            typeof v === 'boolean'
                              ? v
                                ? 'text-green-600'
                                : 'text-muted-foreground'
                              : ''
                          }
                        >
                          {typeof v === 'boolean' ? (v ? 'Yes' : 'No') : String(v)}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-muted-foreground">Loading...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
