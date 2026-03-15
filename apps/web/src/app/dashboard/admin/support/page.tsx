'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

export default function AdminSupportPage() {
  const { toast } = useToast();
  const [userId, setUserId] = useState('');
  const [context, setContext] = useState<{
    user: { id: string; email: string; display_name: string | null; is_active: boolean };
    projects_count: number;
    books_count: number;
  } | null>(null);

  const fetchContext = () => {
    if (!userId.trim()) return;
    api<typeof context>(`/api/v1/admin/support/user-context/${userId}`)
      .then(setContext)
      .catch(() => {
        toast({ title: 'User not found', variant: 'destructive' });
        setContext(null);
      });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Support tools</h1>
        <p className="text-muted-foreground mt-1">User context for support requests.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <h2 className="font-semibold">User context</h2>
          <p className="text-sm text-muted-foreground">Enter user ID to fetch context.</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="User ID (UUID)"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="max-w-md"
            />
            <Button onClick={fetchContext}>Fetch</Button>
          </div>
          {context && (
            <pre className="rounded bg-muted p-4 text-sm overflow-auto">
              {JSON.stringify(context, null, 2)}
            </pre>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
