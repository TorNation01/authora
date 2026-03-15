'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { api } from '@/lib/api';

export default function AdminGamificationPage() {
  const [data, setData] = useState<{
    badges: Array<{
      id: string;
      name: string;
      description: string | null;
      category: string;
      xp_reward: number;
      criteria_type: string;
    }>;
  } | null>(null);

  useEffect(() => {
    api<typeof data>('/api/v1/admin/gamification').then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Gamification</h1>
        <p className="text-muted-foreground mt-1">Badge definitions and gamification rules.</p>
      </div>

      <Card variant="soft">
        <CardContent className="pt-6">
          {data?.badges?.length ? (
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">ID</th>
                    <th className="text-left p-3">Name</th>
                    <th className="text-left p-3">Category</th>
                    <th className="text-left p-3">XP</th>
                    <th className="text-left p-3">Criteria</th>
                  </tr>
                </thead>
                <tbody>
                  {data.badges.map((b) => (
                    <tr key={b.id} className="border-t">
                      <td className="p-3 font-mono">{b.id}</td>
                      <td className="p-3">{b.name}</td>
                      <td className="p-3">{b.category}</td>
                      <td className="p-3">{b.xp_reward}</td>
                      <td className="p-3">{b.criteria_type}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-muted-foreground">No badge definitions. Run seed to populate.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
