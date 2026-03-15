'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function AdminFeatureFlagsPage() {
  const { toast } = useToast();
  const [data, setData] = useState<{
    db_flags: Array<{ key: string; enabled: boolean; rules: unknown }>;
    env_flags: Record<string, boolean>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/feature-flags')
      .then(setData)
      .catch(() => toast({ title: 'Failed to load', variant: 'destructive' }));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Feature flags</h1>
        <p className="text-muted-foreground mt-1">Environment and database flags.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Environment flags</h2>
          <p className="text-sm text-muted-foreground">Set via FEATURE_* env vars.</p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2">
            {data?.env_flags &&
              Object.entries(data.env_flags).map(([key, enabled]) => (
                <div key={key} className="flex items-center justify-between rounded border p-3">
                  <span className="font-mono text-sm">{key}</span>
                  <span className={enabled ? 'text-green-600' : 'text-muted-foreground'}>
                    {enabled ? 'On' : 'Off'}
                  </span>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">Database flags</h2>
          <p className="text-sm text-muted-foreground">Stored in settings (feature.* keys).</p>
        </CardHeader>
        <CardContent>
          {data?.db_flags?.length ? (
            <div className="space-y-2">
              {data.db_flags.map((f) => (
                <div key={f.key} className="flex items-center justify-between rounded border p-3">
                  <span className="font-mono text-sm">{f.key}</span>
                  <span className={f.enabled ? 'text-green-600' : 'text-muted-foreground'}>
                    {f.enabled ? 'On' : 'Off'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No database flags.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
