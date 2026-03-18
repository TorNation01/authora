'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { Loader2, BookOpen, Users, Zap } from 'lucide-react';

type NetworkMetrics = {
  period_days: number;
  templates_driving_usage: {
    template_id: string;
    slug: string;
    name: string;
    creator_id: string | null;
    creator_name: string | null;
    usage_count: number;
  }[];
  creators_driving_signups: {
    creator_id: string;
    creator_name: string | null;
    signups: number;
  }[];
  features_driving_retention: {
    period_days: number;
    events: Record<string, number>;
  };
};

export default function AdminNetworkMetricsPage() {
  const [data, setData] = useState<NetworkMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  useEffect(() => {
    setLoading(true);
    api<NetworkMetrics>(`/api/v1/growth/admin/network-metrics?days=${days}`)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [days]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Network metrics</h1>
        <p className="text-muted-foreground">Unable to load network metrics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Network metrics</h1>
          <p className="text-muted-foreground mt-1">
            Templates driving usage, creators driving signups, features driving retention.
          </p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded border bg-background px-3 py-1.5 text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Templates driving usage
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Templates with most projects + purchases in the period
            </p>
          </CardHeader>
          <CardContent>
            {data.templates_driving_usage.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data yet.</p>
            ) : (
              <div className="space-y-2">
                {data.templates_driving_usage.map((t) => (
                  <div
                    key={t.template_id}
                    className="flex items-center justify-between rounded border p-2 text-sm"
                  >
                    <div>
                      <p className="font-medium">{t.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {t.creator_name || '—'} · {t.slug}
                      </p>
                    </div>
                    <span className="font-medium">{t.usage_count} uses</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Creators driving signups
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Creators whose referral links drove signups
            </p>
          </CardHeader>
          <CardContent>
            {data.creators_driving_signups.length === 0 ? (
              <p className="text-sm text-muted-foreground">No data yet.</p>
            ) : (
              <div className="space-y-2">
                {data.creators_driving_signups.map((c) => (
                  <div
                    key={c.creator_id}
                    className="flex items-center justify-between rounded border p-2 text-sm"
                  >
                    <p className="font-medium">{c.creator_name || c.creator_id}</p>
                    <span className="font-medium">{c.signups} signups</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Features driving retention
          </CardTitle>
          <p className="text-sm text-muted-foreground">
            First-time activation events in the period
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-4">
            {Object.entries(data.features_driving_retention.events || {}).map(
              ([event, count]) => (
                <div
                  key={event}
                  className="rounded border p-3 text-sm"
                >
                  <p className="font-medium text-muted-foreground">
                    {event.replace(/_/g, ' ')}
                  </p>
                  <p className="text-xl font-bold">{count}</p>
                </div>
              )
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
