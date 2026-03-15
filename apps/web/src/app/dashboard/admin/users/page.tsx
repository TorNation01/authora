'use client';

import { useCallback, useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';

interface UserRow {
  id: string;
  email: string;
  display_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  billing_exempt: boolean;
  created_at: string | null;
}

export default function AdminUsersPage() {
  const { toast } = useToast();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchUsers = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams({ limit: '50' });
    if (search) params.set('search', search);
    api<{ users: UserRow[]; total: number }>(`/api/v1/admin/users?${params}`)
      .then((data) => {
        setUsers(data.users);
        setTotal(data.total);
      })
      .catch(() => toast({ title: 'Failed to load users', variant: 'destructive' }))
      .finally(() => setLoading(false));
  }, [search, toast]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const toggleActive = async (user: UserRow) => {
    try {
      await api(`/api/v1/admin/users/${user.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_active: !user.is_active }),
      });
      toast({ title: 'Updated' });
      fetchUsers();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    }
  };

  const toggleAdmin = async (user: UserRow) => {
    try {
      await api(`/api/v1/admin/users/${user.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ is_admin: !user.is_admin }),
      });
      toast({ title: 'Updated' });
      fetchUsers();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">User management</h1>
        <p className="text-muted-foreground mt-1">View and manage users.</p>
      </div>

      <Card variant="soft">
        <CardHeader>
          <div className="flex items-center gap-4">
            <Input
              placeholder="Search by email or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="max-w-xs"
            />
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-muted-foreground">Loading...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">{total} users</p>
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-3">Email</th>
                      <th className="text-left p-3">Name</th>
                      <th className="text-left p-3">Active</th>
                      <th className="text-left p-3">Admin</th>
                      <th className="text-left p-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-t">
                        <td className="p-3">{u.email}</td>
                        <td className="p-3">{u.display_name || '—'}</td>
                        <td className="p-3">{u.is_active ? 'Yes' : 'No'}</td>
                        <td className="p-3">{u.is_admin ? 'Yes' : 'No'}</td>
                        <td className="p-3 flex gap-2">
                          <Button variant="outline" size="sm" onClick={() => toggleActive(u)}>
                            {u.is_active ? 'Deactivate' : 'Activate'}
                          </Button>
                          <Button variant="outline" size="sm" onClick={() => toggleAdmin(u)}>
                            {u.is_admin ? 'Remove admin' : 'Make admin'}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
