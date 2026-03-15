'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminExportJobsPage() {
  const [data, setData] = useState<{
    jobs: Array<{
      id: string;
      user_id: string;
      book_id: string;
      format: string;
      status: string;
      error_message: string | null;
      created_at: string | null;
      completed_at: string | null;
    }>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/export-jobs').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Export jobs</h1>
        <p className="text-muted-foreground mt-1">Export job status and history.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data?.jobs?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">Format</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-left p-3">Created</th>
                    <th className="text-left p-3">Error</th>
                  </tr>
                </thead>
                <tbody>
                  {data.jobs.map((j) => (
                    <tr key={j.id} className="border-t">
                      <td className="p-3">{j.format}</td>
                      <td className="p-3">{j.status}</td>
                      <td className="p-3">{j.created_at ?? '—'}</td>
                      <td className="p-3 text-muted-foreground">{j.error_message ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No export jobs. Exports are currently synchronous.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
