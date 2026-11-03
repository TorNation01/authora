'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { api } from '@/lib/api';
import { TrendingUp, UserPlus, BookCheck, CreditCard, UserMinus, Loader2 } from 'lucide-react';

type GrowthData = {
  period_days: number;
  since: string;
  generated_at: string;
  funnel: {
    signups: number;
    trials_started: number;
    first_book_completed: number;
    conversions: number;
  };
  conversion: {
    signup_to_paid_pct: number | null;
    trial_to_paid_pct: number | null;
    trials_active_now: number;
    converted_from_window_trials: number;
  };
  churn: {
    paying_at_period_start: number;
    paying_now: number;
    churned_in_window: number;
    churn_pct: number | null;
    pending_cancellations: number;
  };
  revenue: {
    mrr_cents: number;
    paying_customers: number;
    arpu_cents: number | null;
  };
  books: { first_book_completed_total: number; completed_book_ids: string[] };
  series: Array<{ day: string; signups: number; trials: number; conversions: number }>;
  definitions: Record<string, string>;
};

const money = (cents: number | null) =>
  cents == null ? '—' : `$${(cents / 100).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
const pctText = (p: number | null) => (p == null ? '—' : `${p.toFixed(1)}%`);

function Kpi({
  label,
  value,
  sub,
  icon: Icon,
  tone = 'default',
}: {
  label: string;
  value: string | number;
  sub?: string;
  icon: React.ComponentType<{ className?: string }>;
  tone?: 'default' | 'good' | 'warn';
}) {
  const toneClass =
    tone === 'good' ? 'text-emerald-500' : tone === 'warn' ? 'text-amber-500' : 'text-primary';
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription className="flex items-center gap-2 text-xs uppercase tracking-wide">
          <Icon className={`h-4 w-4 ${toneClass}`} />
          {label}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-semibold tabular-nums text-foreground">{value}</p>
        {sub && <p className="mt-1 text-xs text-muted-foreground">{sub}</p>}
      </CardContent>
    </Card>
  );
}

export default function AdminGrowthPage() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<GrowthData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setData(null);
    api<GrowthData>(`/api/v1/admin/metrics/growth?days=${days}`)
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch(() => setError('Could not load growth metrics. Admin access required.'));
  }, [days]);

  const activeDays = data?.series.filter(
    (d) => d.signups || d.trials || d.conversions
  ) ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="flex items-center gap-2 text-2xl font-semibold text-foreground">
            <TrendingUp className="h-6 w-6 text-primary" />
            Growth
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Live from the Authora database — signup, trial, first completed book, paid, churn.
          </p>
        </div>
        <div className="flex gap-2">
          {[7, 30, 90].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`rounded-md border px-3 py-1.5 text-sm transition ${
                days === d
                  ? 'border-primary bg-primary/10 text-primary'
                  : 'border-border text-muted-foreground hover:border-primary/40'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {error && (
        <Card>
          <CardContent className="pt-6 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {!data && !error && (
        <Card>
          <CardContent className="flex items-center gap-3 pt-6 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" /> Reading the database…
          </CardContent>
        </Card>
      )}

      {data && (
        <>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Kpi
              label="Signups"
              value={data.funnel.signups}
              sub={`last ${data.period_days} days`}
              icon={UserPlus}
            />
            <Kpi
              label="First book completed"
              value={data.funnel.first_book_completed}
              sub="earliest finished draft inside the window"
              icon={BookCheck}
              tone="good"
            />
            <Kpi
              label="Conversions"
              value={pctText(data.conversion.trial_to_paid_pct)}
              sub={`${data.funnel.conversions} paid starts · ${data.conversion.trials_active_now} trials live now`}
              icon={CreditCard}
            />
            <Kpi
              label="Churn"
              value={pctText(data.churn.churn_pct)}
              sub={`${data.churn.churned_in_window} lost of ${data.churn.paying_at_period_start} paying at period start`}
              icon={UserMinus}
              tone={(data.churn.churn_pct ?? 0) > 5 ? 'warn' : 'default'}
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Funnel, in order</CardTitle>
              <CardDescription>
                Each step counts real rows, not events: users, trial stamps, complete drafts,
                subscriptions.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { label: 'Signed up', n: data.funnel.signups, of: null as number | null },
                { label: 'Trial started', n: data.funnel.trials_started, of: data.funnel.signups },
                { label: 'First book completed', n: data.funnel.first_book_completed, of: data.funnel.trials_started },
                { label: 'Paid', n: data.funnel.conversions, of: data.funnel.trials_started },
              ].map((step, i) => {
                const width = data.funnel.signups
                  ? Math.max(2, Math.round((step.n / data.funnel.signups) * 100))
                  : 0;
                const rate = step.of ? (step.n / step.of) * 100 : null;
                return (
                  <div key={step.label}>
                    <div className="mb-1 flex items-baseline justify-between text-sm">
                      <span className="text-foreground">
                        <span className="mr-2 text-xs text-muted-foreground">{i + 1}</span>
                        {step.label}
                      </span>
                      <span className="tabular-nums text-muted-foreground">
                        {step.n}
                        {rate != null && ` · ${rate.toFixed(0)}% of prev`}
                      </span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary/70"
                        style={{ width: `${width}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>

          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>MRR</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold tabular-nums">{money(data.revenue.mrr_cents)}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  {data.revenue.paying_customers} paying · ARPU {money(data.revenue.arpu_cents)}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Signup → paid</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold tabular-nums">
                  {pctText(data.conversion.signup_to_paid_pct)}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  accounts created in window that hold a subscription
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Pending churn</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-semibold tabular-nums">
                  {data.churn.pending_cancellations}
                </p>
                <p className="mt-1 text-xs text-muted-foreground">
                  paid but set to cancel at period end
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Days with activity</CardTitle>
              <CardDescription>
                {activeDays.length
                  ? `${activeDays.length} of the last ${data.period_days} days`
                  : `No signups, trials or conversions in the last ${data.period_days} days`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {activeDays.length > 0 && (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-xs uppercase tracking-wide text-muted-foreground">
                      <th className="py-2 font-medium">Day</th>
                      <th className="py-2 text-right font-medium">Signups</th>
                      <th className="py-2 text-right font-medium">Trials</th>
                      <th className="py-2 text-right font-medium">Conversions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {activeDays.map((d) => (
                      <tr key={d.day} className="border-b border-border/50 last:border-0">
                        <td className="py-2 text-foreground">{d.day}</td>
                        <td className="py-2 text-right tabular-nums">{d.signups}</td>
                        <td className="py-2 text-right tabular-nums">{d.trials}</td>
                        <td className="py-2 text-right tabular-nums">{d.conversions}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">How each number is counted</CardTitle>
              <CardDescription>
                Printed from the API response so the page can never drift from the query.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-xs text-muted-foreground">
              {Object.entries(data.definitions).map(([k, v]) => (
                <p key={k}>
                  <span className="font-medium text-foreground">{k}</span> — {v}
                </p>
              ))}
              <p className="pt-2">Snapshot {new Date(data.generated_at).toLocaleString()} · window starts {new Date(data.since).toLocaleString()}</p>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
