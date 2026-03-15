'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminEncouragementPage() {
  const [data, setData] = useState<{
    encouragement: string[];
    recovery_nudges: string[];
    celebration: Record<string, string[]>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/encouragement-messages').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Encouragement messages</h1>
        <p className="text-muted-foreground mt-1">Message libraries from content/messages.py.</p>
      </div>

      {data && (
        <div className="space-y-4">
          <Card variant="soft">
            <CardHeader>
              <h2 className="font-semibold">Encouragement ({data.encouragement?.length ?? 0})</h2>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {data.encouragement?.slice(0, 5).map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
                {(data.encouragement?.length ?? 0) > 5 && (
                  <li className="text-muted-foreground">... and {(data.encouragement?.length ?? 0) - 5} more</li>
                )}
              </ul>
            </CardContent>
          </Card>
          <Card variant="soft">
            <CardHeader>
              <h2 className="font-semibold">Recovery nudges ({data.recovery_nudges?.length ?? 0})</h2>
            </CardHeader>
            <CardContent>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {data.recovery_nudges?.slice(0, 3).map((m, i) => (
                  <li key={i}>{m}</li>
                ))}
                {(data.recovery_nudges?.length ?? 0) > 3 && (
                  <li className="text-muted-foreground">... and {(data.recovery_nudges?.length ?? 0) - 3} more</li>
                )}
              </ul>
            </CardContent>
          </Card>
          <Card variant="soft">
            <CardHeader>
              <h2 className="font-semibold">Celebration (by category)</h2>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {data.celebration && Object.entries(data.celebration).map(([cat, msgs]) => (
                  <div key={cat}>
                    <p className="font-medium text-sm">{cat}</p>
                    <p className="text-muted-foreground text-sm">{msgs?.length ?? 0} messages</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
