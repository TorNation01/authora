'use client';

import { useCallback, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
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
  const [notes, setNotes] = useState('');
  const [notesSaving, setNotesSaving] = useState(false);

  const fetchContext = useCallback(() => {
    if (!userId.trim()) return;
    Promise.all([
      api<typeof context>(`/api/v1/admin/support/user-context/${userId}`),
      api<{ notes: string }>(`/api/v1/admin/support/notes/${userId}`),
    ])
      .then(([ctx, notesRes]) => {
        setContext(ctx);
        setNotes(notesRes.notes || '');
      })
      .catch(() => {
        toast({ title: 'User not found', variant: 'destructive' });
        setContext(null);
        setNotes('');
      });
  }, [userId, toast]);

  const saveNotes = async () => {
    if (!userId.trim()) return;
    setNotesSaving(true);
    try {
      await api(`/api/v1/admin/support/notes/${userId}`, {
        method: 'PUT',
        body: JSON.stringify({ notes }),
      });
      toast({ title: 'Notes saved' });
    } catch {
      toast({ title: 'Failed to save', variant: 'destructive' });
    } finally {
      setNotesSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Support tools</h1>
        <p className="text-muted-foreground mt-1">
          User context and support notes for support requests.
        </p>
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

      {userId.trim() && (
        <Card variant="soft">
          <CardHeader>
            <h2 className="font-semibold">Support notes</h2>
            <p className="text-sm text-muted-foreground">
              Internal notes for this user. Not visible to the user.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Add support notes..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={6}
              className="resize-none"
            />
            <Button onClick={saveNotes} disabled={notesSaving}>
              {notesSaving ? 'Saving...' : 'Save notes'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
