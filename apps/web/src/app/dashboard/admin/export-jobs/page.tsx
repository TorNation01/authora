'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { AlertTriangle } from 'lucide-react';

const STATUS_OPTIONS = [
  { value: '', label: 'All' },
  { value: 'pending', label: 'Pending' },
  { value: 'processing', label: 'Processing' },
  { value: 'completed', label: 'Completed' },
  { value: 'failed', label: 'Failed' },
];

export default function AdminExportJobsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const statusFilter = searchParams.get('status') || '';
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
    const params = new URLSearchParams();
    if (statusFilter) params.set('status_filter', statusFilter);
    api<typeof data>(`/api/v1/admin/export-jobs?${params}`).then(setData).catch(() => setData(null));
  }, [statusFilter]);

  const failedCount = data?.jobs?.filter((j) => j.status === 'failed').length ?? 0;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Export jobs</h1>
        <p className="text-muted-foreground mt-1">Export job status and history.</p>
      </div>

      {failedCount > 0 && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/5 p-4 flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-destructive" />
          <span className="text-sm font-medium">
            {failedCount} failed job{failedCount !== 1 ? 's' : ''}
          </span>
        </div>
      )}

      <Card variant="soft">
        <CardContent className="pt-6 space-y-4">
          <div className="flex flex-wrap gap-2">
            {STATUS_OPTIONS.map((opt) => (
              <Button
                key={opt.value || 'all'}
                variant={statusFilter === opt.value ? 'default' : 'outline'}
                size="sm"
                onClick={() =>
                  router.push(
                    opt.value ? `/dashboard/admin/export-jobs?status=${opt.value}` : '/dashboard/admin/export-jobs'
                  )
                }
              >
                {opt.label}
              </Button>
            ))}
          </div>
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
                    <tr
                      key={j.id}
                      className={`border-t ${j.status === 'failed' ? 'bg-destructive/5' : ''}`}
                    >
                      <td className="p-3">{j.format}</td>
                      <td className="p-3">
                        <span
                          className={
                            j.status === 'failed'
                              ? 'text-destructive font-medium'
                              : j.status === 'completed'
                                ? 'text-green-600'
                                : ''
                          }
                        >
                          {j.status}
                        </span>
                      </td>
                      <td className="p-3">{j.created_at ?? '—'}</td>
                      <td className="p-3 text-muted-foreground max-w-xs truncate" title={j.error_message ?? ''}>
                        {j.error_message ?? '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">
              {statusFilter
                ? `No ${statusFilter} export jobs.`
                : 'No export jobs. Exports are currently synchronous.'}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
