'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';
import { Loader2, BookOpen, TrendingUp, DollarSign, CheckCircle, XCircle, Clock } from 'lucide-react';

type CreatorStatus = {
  status: string | null;
  is_creator: boolean;
  applied_at?: string;
  approved_at?: string;
  rejected_at?: string;
  rejection_reason?: string;
};

type DashboardData = {
  profile: {
    id: string;
    status: string;
    applied_at?: string;
    approved_at?: string;
  };
  can_access_dashboard: boolean;
  submissions?: Array<{
    id: string;
    slug: string;
    name: string;
    description: string | null;
    category: string | null;
    price_cents: number | null;
    status: string;
    approved_template_id: string | null;
    created_at: string;
    reviewed_at: string | null;
    rejected_reason: string | null;
  }>;
};

export default function CreatorPage() {
  const { toast } = useToast();
  const [status, setStatus] = useState<CreatorStatus | null>(null);
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState(false);
  const [applicationNote, setApplicationNote] = useState('');

  useEffect(() => {
    Promise.all([
      api<CreatorStatus>('/api/v1/creators/status'),
      api<DashboardData>('/api/v1/creators/dashboard').catch(() => null),
    ])
      .then(([s, d]) => {
        setStatus(s);
        setDashboard(d ?? null);
      })
      .catch(() => setStatus(null))
      .finally(() => setLoading(false));
  }, []);

  const handleApply = async () => {
    setApplying(true);
    try {
      await api('/api/v1/creators/apply', {
        method: 'POST',
        body: JSON.stringify({ application_note: applicationNote || undefined }),
      });
      toast({ title: 'Application submitted', description: 'You will be notified when reviewed.' });
      setApplicationNote('');
      const s = await api<CreatorStatus>('/api/v1/creators/status');
      setStatus(s);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Failed to apply';
      toast({ title: msg, variant: 'destructive' });
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (status?.status === 'rejected') {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Creator program</h1>
          <p className="text-muted-foreground mt-1">Your application was not approved.</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <XCircle className="h-5 w-5 text-destructive" />
              Application rejected
            </CardTitle>
            <CardDescription>
              {status.rejection_reason || 'Your application was not approved at this time.'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Rejected: {status.rejected_at ? new Date(status.rejected_at).toLocaleDateString() : '—'}
            </p>
            <p className="text-sm mt-2">You may re-apply with additional information.</p>
            <Button className="mt-4" onClick={() => window.location.reload()}>
              Try again
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status?.status === 'pending') {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Creator program</h1>
          <p className="text-muted-foreground mt-1">Your application is under review.</p>
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-amber-500" />
              Application pending
            </CardTitle>
            <CardDescription>
              We will notify you when your application has been reviewed.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Applied: {status.applied_at ? new Date(status.applied_at).toLocaleDateString() : '—'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status?.is_creator && dashboard?.can_access_dashboard) {
    const submissions = dashboard.submissions ?? [];
    const pending = submissions.filter((s) => s.status === 'pending').length;
    const approved = submissions.filter((s) => s.status === 'approved').length;

    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold">Creator dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Manage your templates and view performance.
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">My templates</CardTitle>
              <BookOpen className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{submissions.length}</div>
              <p className="text-xs text-muted-foreground">
                {pending} pending · {approved} approved
              </p>
              <Button variant="outline" size="sm" className="mt-2" asChild>
                <Link href="/dashboard/creator/templates">Manage</Link>
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Performance</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">View usage and sales</p>
              <Button variant="outline" size="sm" className="mt-2" asChild>
                <Link href="/dashboard/creator/performance">View stats</Link>
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Earnings</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">Balance and payouts</p>
              <Button variant="outline" size="sm" className="mt-2" asChild>
                <Link href="/dashboard/creator/earnings">View earnings</Link>
              </Button>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Status</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <p className="text-sm font-medium text-green-600">Approved creator</p>
              <p className="text-xs text-muted-foreground">
                Since {dashboard.profile.approved_at ? new Date(dashboard.profile.approved_at).toLocaleDateString() : '—'}
              </p>
            </CardContent>
          </Card>
        </div>

        {submissions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent submissions</CardTitle>
              <CardDescription>Your template submissions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {submissions.slice(0, 5).map((s) => (
                  <div
                    key={s.id}
                    className="flex items-center justify-between rounded border p-3"
                  >
                    <div>
                      <p className="font-medium">{s.name}</p>
                      <p className="text-sm text-muted-foreground">{s.slug}</p>
                    </div>
                    <span
                      className={`text-xs font-medium px-2 py-1 rounded ${
                        s.status === 'approved'
                          ? 'bg-green-500/10 text-green-600'
                          : s.status === 'rejected'
                            ? 'bg-destructive/10 text-destructive'
                            : 'bg-amber-500/10 text-amber-600'
                      }`}
                    >
                      {s.status}
                    </span>
                  </div>
                ))}
              </div>
              <Button variant="outline" className="mt-4" asChild>
                <Link href="/dashboard/creator/templates">View all</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Become a creator</h1>
        <p className="text-muted-foreground mt-1">
          Create and sell templates on AUTHORA. Share your writing frameworks with the community.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Apply to the creator program</CardTitle>
          <CardDescription>
            Tell us about yourself and why you want to create templates. Our team will review your
            application.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium">Application note (optional)</label>
            <Textarea
              className="mt-1"
              placeholder="Share your experience, what templates you plan to create, or any relevant links..."
              value={applicationNote}
              onChange={(e) => setApplicationNote(e.target.value)}
              rows={4}
            />
          </div>
          <Button onClick={handleApply} disabled={applying}>
            {applying ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Apply now'
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
