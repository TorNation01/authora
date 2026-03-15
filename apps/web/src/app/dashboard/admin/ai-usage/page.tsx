'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';

export default function AdminAIUsagePage() {
  const [period, setPeriod] = useState(new Date().toISOString().slice(0, 7));
  const [data, setData] = useState<{ period: string; rows: Array<{ user_id: string; metric: string; total: number }> } | null>(null);

  useEffect(() => {
    api<typeof data>(`/api/v1/admin/ai-usage?period=${period}`)
      .then(setData)
      .catch(() => setData(null));
  }, [period]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI usage</h1>
        <p className="text-muted-foreground mt-1">Usage records by user and period.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <Input
            type="month"
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="max-w-xs"
          />
        </CardHeader>
        <CardContent>
          {data?.rows?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">User ID</th>
                    <th className="text-left p-3">Metric</th>
                    <th className="text-left p-3">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {data.rows.map((r, i) => (
                    <tr key={i} className="border-t">
                      <td className="p-3 font-mono text-xs">{r.user_id}</td>
                      <td className="p-3">{r.metric}</td>
                      <td className="p-3">{r.total}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No usage data for this period.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
