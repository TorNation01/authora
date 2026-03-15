'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminErrorsPage() {
  const [data, setData] = useState<{
    message: string;
    suggestions?: string[];
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/errors').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Error monitoring</h1>
        <p className="text-muted-foreground mt-1">Configure log aggregation for persisted errors.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data ? (
            <div className="space-y-4">
              <p>{data.message}</p>
              {data.suggestions?.length && (
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  {data.suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
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
