'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminSetupPage() {
  const [data, setData] = useState<{ state: Record<string, unknown> } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/setup-state').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Setup state</h1>
        <p className="text-muted-foreground mt-1">Setup wizard state and config.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data ? (
            <pre className="rounded bg-muted p-4 text-xs overflow-auto">
              {JSON.stringify(data.state, null, 2)}
            </pre>
          ) : (
            <p className="text-muted-foreground">Loading...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
