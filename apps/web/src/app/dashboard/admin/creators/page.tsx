'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Check, X, Star } from 'lucide-react';

type Creator = {
  id: string;
  user_id: string;
  email: string;
  status: string;
  is_featured?: boolean;
  application_note: string | null;
  applied_at: string | null;
  approved_at: string | null;
  rejected_at: string | null;
  rejection_reason: string | null;
};

export default function AdminCreatorsPage() {
  const { toast } = useToast();
  const [creators, setCreators] = useState<Creator[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [acting, setActing] = useState<Record<string, boolean>>({});

  const fetchCreators = () => {
    setLoading(true);
    const q = statusFilter ? `?status=${statusFilter}` : '';
    api<Creator[]>(`/api/v1/admin/creators${q}`)
      .then(setCreators)
      .catch(() => setCreators([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchCreators();
  }, [statusFilter]);

  const handleApprove = async (id: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creators/${id}/approve`, { method: 'POST' });
      toast({ title: 'Creator approved' });
      fetchCreators();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to approve';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleReject = async (id: string, reason?: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creators/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ rejection_reason: reason || undefined }),
      });
      toast({ title: 'Creator rejected' });
      fetchCreators();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to reject';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleSetFeatured = async (id: string, isFeatured: boolean) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/creators/${id}/featured`, {
        method: 'PATCH',
        body: JSON.stringify({ is_featured: isFeatured }),
      });
      toast({ title: isFeatured ? 'Creator featured' : 'Creator unfeatured' });
      fetchCreators();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to update';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Creator applications</h1>
        <p className="text-muted-foreground mt-1">
          Review and approve users who want to sell templates on the platform.
        </p>
      </div>

      <div className="flex gap-2">
        <Button
          variant={statusFilter === '' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setStatusFilter('')}
        >
          All
        </Button>
        <Button
          variant={statusFilter === 'pending' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setStatusFilter('pending')}
        >
          Pending
        </Button>
        <Button
          variant={statusFilter === 'approved' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setStatusFilter('approved')}
        >
          Approved
        </Button>
        <Button
          variant={statusFilter === 'rejected' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setStatusFilter('rejected')}
        >
          Rejected
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Creators</h2>
          </CardHeader>
          <CardContent>
            {creators.length === 0 ? (
              <p className="text-muted-foreground py-8 text-center">No creators found.</p>
            ) : (
              <div className="space-y-4">
                {creators.map((c) => (
                  <div
                    key={c.id}
                    className="flex items-center justify-between rounded-lg border p-4"
                  >
                    <div>
                      <p className="font-medium">{c.email}</p>
                      <p className="text-sm text-muted-foreground">
                        Applied: {c.applied_at ? new Date(c.applied_at).toLocaleDateString() : '—'}
                      </p>
                      {c.application_note && (
                        <p className="text-sm mt-1 text-muted-foreground">{c.application_note}</p>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {c.status === 'approved' && (
                        <Button
                          size="sm"
                          variant={c.is_featured ? 'default' : 'outline'}
                          onClick={() => handleSetFeatured(c.id, !c.is_featured)}
                          disabled={acting[c.id]}
                          title={c.is_featured ? 'Unfeature' : 'Feature'}
                        >
                          <Star className={`h-4 w-4 ${c.is_featured ? 'fill-current' : ''}`} />
                        </Button>
                      )}
                      <Badge
                        variant={
                          c.status === 'approved'
                            ? 'default'
                            : c.status === 'rejected'
                              ? 'destructive'
                              : 'secondary'
                        }
                      >
                        {c.status}
                      </Badge>
                      {c.status === 'pending' && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => handleApprove(c.id)}
                            disabled={acting[c.id]}
                          >
                            {acting[c.id] ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Check className="h-4 w-4" />
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleReject(c.id)}
                            disabled={acting[c.id]}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
