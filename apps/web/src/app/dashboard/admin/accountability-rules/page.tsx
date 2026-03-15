'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminAccountabilityRulesPage() {
  const [data, setData] = useState<{
    accountability_styles?: string[];
    plan_statuses?: string[];
    recovery_plan_types?: string[];
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/accountability-rules')
      .then(setData)
      .catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Accountability rules</h1>
        <p className="text-muted-foreground mt-1">
          Read-only view of accountability engine constants. Edit in code.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Card variant="soft">
          <CardHeader>
            <h2 className="font-semibold">Accountability styles</h2>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1">
              {data?.accountability_styles?.map((s) => (
                <li key={s} className="text-muted-foreground">
                  {s}
                </li>
              )) ?? <li className="text-muted-foreground">—</li>}
            </ul>
          </CardContent>
        </Card>
        <Card variant="soft">
          <CardHeader>
            <h2 className="font-semibold">Plan statuses</h2>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1">
              {data?.plan_statuses?.map((s) => (
                <li key={s} className="text-muted-foreground">
                  {s}
                </li>
              )) ?? <li className="text-muted-foreground">—</li>}
            </ul>
          </CardContent>
        </Card>
        <Card variant="soft">
          <CardHeader>
            <h2 className="font-semibold">Recovery plan types</h2>
          </CardHeader>
          <CardContent>
            <ul className="text-sm space-y-1">
              {data?.recovery_plan_types?.map((s) => (
                <li key={s} className="text-muted-foreground">
                  {s}
                </li>
              )) ?? <li className="text-muted-foreground">—</li>}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
