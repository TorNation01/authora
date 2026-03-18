'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Check, X, MessageSquare } from 'lucide-react';

type Submission = {
  id: string;
  creator_id: string;
  creator_email: string;
  slug: string;
  name: string;
  description: string | null;
  category: string | null;
  price_cents: number | null;
  status: string;
  payload: Record<string, unknown> | null;
  created_at: string | null;
  reviewed_at: string | null;
  rejected_reason: string | null;
  change_request_reason: string | null;
};

export default function AdminTemplateSubmissionsPage() {
  const { toast } = useToast();
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [acting, setActing] = useState<Record<string, boolean>>({});
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [requestChangesId, setRequestChangesId] = useState<string | null>(null);
  const [changeReason, setChangeReason] = useState('');

  const fetchSubmissions = () => {
    setLoading(true);
    const q = statusFilter ? `?status=${statusFilter}` : '';
    api<Submission[]>(`/api/v1/admin/template-submissions${q}`)
      .then(setSubmissions)
      .catch(() => setSubmissions([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchSubmissions();
  }, [statusFilter]);

  const handleApprove = async (id: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      const res = await api<{ id: string; slug: string; name: string }>(
        `/api/v1/admin/template-submissions/${id}/approve`,
        { method: 'POST' }
      );
      toast({ title: 'Template approved', description: `Created "${res.name}"` });
      fetchSubmissions();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to approve';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleRequestChanges = async (id: string) => {
    if (!changeReason.trim()) return;
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/template-submissions/${id}/request-changes`, {
        method: 'POST',
        body: JSON.stringify({ change_request_reason: changeReason.trim() }),
      });
      toast({ title: 'Changes requested', description: 'Creator can edit and resubmit.' });
      setRequestChangesId(null);
      setChangeReason('');
      fetchSubmissions();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const handleReject = async (id: string, reason?: string) => {
    setActing((p) => ({ ...p, [id]: true }));
    try {
      await api(`/api/v1/admin/template-submissions/${id}/reject`, {
        method: 'POST',
        body: JSON.stringify({ rejection_reason: reason || undefined }),
      });
      toast({ title: 'Submission rejected' });
      fetchSubmissions();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to reject';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setActing((p) => ({ ...p, [id]: false }));
    }
  };

  const toggleExpand = (id: string) => {
    setExpanded((p) => ({ ...p, [id]: !p[id] }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Template submissions</h1>
        <p className="text-muted-foreground mt-1">
          Review creator template submissions. Approve to publish as live templates.
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
        <Button
          variant={statusFilter === 'changes_requested' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setStatusFilter('changes_requested')}
        >
          Changes requested
        </Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">Submissions</h2>
          </CardHeader>
          <CardContent>
            {submissions.length === 0 ? (
              <p className="text-muted-foreground py-8 text-center">No submissions found.</p>
            ) : (
              <div className="space-y-4">
                {submissions.map((s) => (
                  <div
                    key={s.id}
                    className="rounded-lg border p-4 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{s.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {s.slug} · {s.creator_email}
                        </p>
                        {s.description && (
                          <p className="text-sm mt-1 text-muted-foreground line-clamp-2">
                            {s.description}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-1">
                          Category: {s.category || '—'} · Price: {s.price_cents != null ? `$${(s.price_cents / 100).toFixed(2)}` : 'Free'}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={
                            s.status === 'approved'
                              ? 'default'
                              : s.status === 'rejected'
                                ? 'destructive'
                                : s.status === 'changes_requested'
                                  ? 'outline'
                                  : 'secondary'
                          }
                        >
                          {s.status.replace('_', ' ')}
                        </Badge>
                        {(s.status === 'pending' || s.status === 'changes_requested') && (
                          <>
                            <Button
                              size="sm"
                              onClick={() => handleApprove(s.id)}
                              disabled={acting[s.id]}
                            >
                              {acting[s.id] ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Check className="h-4 w-4" />
                              )}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => setRequestChangesId(requestChangesId === s.id ? null : s.id)}
                              disabled={acting[s.id]}
                            >
                              <MessageSquare className="h-4 w-4" />
                            </Button>
                            <Button
                              size="sm"
                              variant="destructive"
                              onClick={() => handleReject(s.id)}
                              disabled={acting[s.id]}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                    {requestChangesId === s.id && (
                      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 space-y-2">
                        <label className="text-sm font-medium">Change request reason (required)</label>
                        <textarea
                          className="w-full rounded border px-3 py-2 text-sm min-h-[80px]"
                          placeholder="Describe what needs to be changed..."
                          value={changeReason}
                          onChange={(e) => setChangeReason(e.target.value)}
                        />
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleRequestChanges(s.id)}
                            disabled={!changeReason.trim() || acting[s.id]}
                          >
                            {acting[s.id] ? <Loader2 className="h-4 w-4 animate-spin" /> : <MessageSquare className="h-4 w-4" />}
                            Request changes
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              setRequestChangesId(null);
                              setChangeReason('');
                            }}
                          >
                            Cancel
                          </Button>
                        </div>
                      </div>
                    )}
                    {s.change_request_reason && (
                      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
                        <p className="text-xs font-medium text-amber-700 dark:text-amber-400">Changes requested</p>
                        <p className="text-sm mt-1">{s.change_request_reason}</p>
                      </div>
                    )}
                    {s.payload && Object.keys(s.payload).length > 0 && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleExpand(s.id)}
                        >
                          {expanded[s.id] ? 'Hide' : 'Show'} payload
                        </Button>
                        {expanded[s.id] && (
                          <pre className="text-xs bg-muted/50 p-3 rounded overflow-auto max-h-48">
                            {JSON.stringify(s.payload, null, 2)}
                          </pre>
                        )}
                      </>
                    )}
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
