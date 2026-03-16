'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { api } from '@/lib/api';
import { TrendingUp, Clock, FileText, BarChart3, Target } from 'lucide-react';

type ActivationData = {
  period_days: number;
  summary: {
    total_users: number;
    activation_rate_pct: number;
    onboarding_completion_rate_pct: number;
    event_counts: Record<string, number>;
  };
  time_to_first_project: Array<{ metric: string; count?: number; value?: number }>;
  time_to_first_chapter: { count: number; median_hours: number; p90_hours: number };
  template_usage: Array<{ template_slug: string; count: number }>;
  mode_selection_rates: Array<{ mode: string; count: number }>;
  starter_path_usage: Array<{ starter_slug: string; count: number }>;
  first_week_retention: { total: number; returned_within_7_days: number; retention_pct: number };
};

export default function AdminActivationPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<ActivationData | null>(null);

  useEffect(() => {
    api<ActivationData>(`/api/v1/admin/activation?days=${days}`)
      .then(setData)
      .catch(() => setData(null));
  }, [days]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Activation analytics</h1>
          <p className="text-muted-foreground mt-1">
            Onboarding completion, time-to-value, template usage, and first-week retention.
          </p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="rounded-md border bg-background px-3 py-2 text-sm"
        >
          <option value={7}>Last 7 days</option>
          <option value={14}>Last 14 days</option>
          <option value={30}>Last 30 days</option>
          <option value={60}>Last 60 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {data ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card variant="soft">
            <CardHeader className="flex flex-row items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              <span>Activation rate</span>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{data.summary.activation_rate_pct}%</p>
              <p className="text-sm text-muted-foreground mt-1">
                Users with first project / {data.summary.total_users} total
              </p>
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader className="flex flex-row items-center gap-2">
              <Target className="h-5 w-5" />
              <span>Onboarding completion</span>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{data.summary.onboarding_completion_rate_pct}%</p>
              <p className="text-sm text-muted-foreground mt-1">
                Completed / started onboarding
              </p>
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader className="flex flex-row items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              <span>First-week retention</span>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{data.first_week_retention.retention_pct}%</p>
              <p className="text-sm text-muted-foreground mt-1">
                {data.first_week_retention.returned_within_7_days} / {data.first_week_retention.total} with first chapter or export
              </p>
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader className="flex flex-row items-center gap-2">
              <Clock className="h-5 w-5" />
              <span>Time to first project</span>
            </CardHeader>
            <CardContent>
              {data.time_to_first_project.find((m) => m.metric === 'median_hours')?.value != null && (
                <>
                  <p className="text-2xl font-bold">
                    {Number(data.time_to_first_project.find((m) => m.metric === 'median_hours')?.value ?? 0).toFixed(1)}h
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">Median (registration → first project)</p>
                </>
              )}
              {!data.time_to_first_project.find((m) => m.metric === 'median_hours')?.value && (
                <p className="text-muted-foreground">No data yet</p>
              )}
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader className="flex flex-row items-center gap-2">
              <FileText className="h-5 w-5" />
              <span>Time to first chapter</span>
            </CardHeader>
            <CardContent>
              {data.time_to_first_chapter.count > 0 ? (
                <>
                  <p className="text-2xl font-bold">{data.time_to_first_chapter.median_hours}h</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Median (first project → first chapter), n={data.time_to_first_chapter.count}
                  </p>
                </>
              ) : (
                <p className="text-muted-foreground">No data yet</p>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card variant="soft">
          <CardContent className="py-8">
            <p className="text-muted-foreground text-center">Loading activation data...</p>
          </CardContent>
        </Card>
      )}

      {data && (
        <div className="grid gap-6 md:grid-cols-2">
          <Card variant="soft">
            <CardHeader>Template usage</CardHeader>
            <CardContent>
              {data.template_usage.length ? (
                <div className="rounded-lg border overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-3">Template</th>
                        <th className="text-right p-3">Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.template_usage.map((r, i) => (
                        <tr key={i} className="border-t">
                          <td className="p-3">{r.template_slug || '(blank)'}</td>
                          <td className="p-3 text-right">{r.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted-foreground">No template usage data.</p>
              )}
            </CardContent>
          </Card>

          <Card variant="soft">
            <CardHeader>Guidance mode selection</CardHeader>
            <CardContent>
              {data.mode_selection_rates.length ? (
                <div className="rounded-lg border overflow-hidden">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-3">Mode</th>
                        <th className="text-right p-3">Count</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.mode_selection_rates.map((r, i) => (
                        <tr key={i} className="border-t">
                          <td className="p-3">{r.mode}</td>
                          <td className="p-3 text-right">{r.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted-foreground">No mode selection data.</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {data && data.starter_path_usage.length > 0 && (
        <Card variant="soft">
          <CardHeader>Starter path usage</CardHeader>
          <CardContent>
            <div className="rounded-lg border overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-muted/50">
                  <tr>
                    <th className="text-left p-3">Starter</th>
                    <th className="text-right p-3">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {data.starter_path_usage.map((r, i) => (
                    <tr key={i} className="border-t">
                      <td className="p-3">{r.starter_slug || '(unknown)'}</td>
                      <td className="p-3 text-right">{r.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
