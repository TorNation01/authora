'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminContentPage() {
  const [data, setData] = useState<{ template_ids: string[] } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/content-templates').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Content templates</h1>
        <p className="text-muted-foreground mt-1">Built-in project templates (fiction/nonfiction).</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Template IDs in content/templates.py</p>
              <div className="flex flex-wrap gap-2">
                {data.template_ids?.map((id) => (
                  <span key={id} className="rounded bg-muted px-2 py-1 text-sm font-mono">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <p className="text-muted-foreground">Loading...</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
