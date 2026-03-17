'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { EmptyState } from '@/components/ui/empty-state';
import { getEmptyStateConfig } from '@/content/empty-states';
import { PageHeader } from '@/components/layout/PageHeader';
import {
  Target,
  Plus,
  Check,
  Calendar,
  Settings,
  Bell,
  Zap,
  BookOpen,
  RotateCcw,
} from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { HelpIcon, HowThisWorks } from '@/components/help';
import {
  ACCOUNTABILITY_PAGE,
  GOALS_COPY,
  STREAK_COPY,
  RECOVERY_COPY,
  REMINDERS_COPY,
  ENCOURAGEMENT_STYLES,
} from '@/content/accountability-copy';

interface Goal {
  id: string;
  target_words: number;
  deadline: string | null;
  completed_at: string | null;
  book_id: string | null;
}

interface Overview {
  daily_goal: number | null;
  weekly_goal: number | null;
  words_today: number;
  words_this_week: number;
  consistency_score: number;
  current_streak: number;
  stuck: boolean;
  plan_paused: boolean;
  next_action: string;
}

interface AccountabilitySettings {
  daily_word_goal: number | null;
  weekly_word_goal: number | null;
  accountability_style: string;
  reminder_enabled: boolean;
  reminder_times: string[] | null;
  timezone: string | null;
  quiet_hours_start: string | null;
  quiet_hours_end: string | null;
  email_reminders_enabled: boolean;
  reminder_cadence: string;
  reminder_types: string[] | null;
  plan_paused: boolean;
  paused_at: string | null;
}

interface RecoveryPlan {
  id: string;
  plan_type: string;
  suggested_daily_words: number | null;
  message: string | null;
  suggested_schedule: Array<{ date: string; target: number }> | null;
  created_at: string;
}

export default function AccountabilityPage() {
  const { toast } = useToast();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [settings, setSettings] = useState<AccountabilitySettings | null>(null);
  const [recoveryPlans, setRecoveryPlans] = useState<RecoveryPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);

  const load = useCallback(async () => {
    try {
      const [g, o, s, r] = await Promise.all([
        api<Goal[]>('/api/v1/goals'),
        api<Overview>('/api/v1/accountability/overview'),
        api<AccountabilitySettings>('/api/v1/accountability/settings'),
        api<RecoveryPlan[]>('/api/v1/accountability/recovery'),
      ]);
      setGoals(g);
      setOverview(o);
      setSettings(s);
      setRecoveryPlans(r);
    } catch {
      setGoals([]);
      setOverview(null);
      setSettings(null);
      setRecoveryPlans([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const updateSettings = useCallback(
    async (patch: Partial<AccountabilitySettings>) => {
      try {
        const s = await api<AccountabilitySettings>('/api/v1/accountability/settings', {
          method: 'PATCH',
          body: JSON.stringify(patch),
        });
        setSettings(s);
        load();
        toast({ title: 'Settings updated' });
      } catch {
        toast({ title: 'Failed to update', variant: 'destructive' });
      }
    },
    [load, toast]
  );

  const sendTestNotification = useCallback(async () => {
    setTestingNotification(true);
    try {
      const res = await api<{ in_app_sent: boolean; email_sent: boolean }>(
        '/api/v1/accountability/notifications/test',
        { method: 'POST' }
      );
      toast({
        title: 'Test sent',
        description: res.in_app_sent
          ? res.email_sent
            ? 'Check your inbox and the bell icon.'
            : 'Check the bell icon for your notification.'
          : 'Notification may not have been delivered.',
      });
    } catch {
      toast({ title: 'Test failed', variant: 'destructive' });
    } finally {
      setTestingNotification(false);
    }
  }, [toast]);

  const acknowledgeRecovery = useCallback(
    async (id: string) => {
      try {
        await api(`/api/v1/accountability/recovery/${id}/acknowledge`, {
          method: 'POST',
        });
        setRecoveryPlans((prev) => prev.filter((p) => p.id !== id));
        toast({ title: 'Recovery plan acknowledged' });
      } catch {
        toast({ title: 'Failed', variant: 'destructive' });
      }
    },
    [toast]
  );

  if (loading) {
    return (
      <div className="p-6 lg:p-8 max-w-4xl">
        <p className="text-muted-foreground">Loading your progress...</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-4xl space-y-8">
      <div className="flex items-start justify-between">
        <PageHeader
          title={ACCOUNTABILITY_PAGE.title}
          description={ACCOUNTABILITY_PAGE.description}
          actions={
            <div className="flex items-center gap-2">
              <HelpIcon
                content={GOALS_COPY.setPace}
                articleId="accountability-overview"
              />
              <Button variant="outline" size="sm" onClick={() => setShowSettings(!showSettings)}>
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </Button>
            </div>
          }
        />
      </div>

      {showSettings && settings && (
        <Card variant="sanctuary">
          <CardHeader>
            <CardTitle>{REMINDERS_COPY.heading}</CardTitle>
            <CardDescription>{REMINDERS_COPY.subheading}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">{REMINDERS_COPY.howWeEncourage}</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {ENCOURAGEMENT_STYLES.map((s) => (
                  <Button
                    key={s.value}
                    variant={settings.accountability_style === s.value ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => updateSettings({ accountability_style: s.value })}
                  >
                    {s.label}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4 flex-wrap">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.reminder_enabled}
                  onChange={(e) => updateSettings({ reminder_enabled: e.target.checked })}
                />
                Enable reminders (opt-in)
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.email_reminders_enabled}
                  onChange={(e) => updateSettings({ email_reminders_enabled: e.target.checked })}
                />
                Email reminders
              </label>
            </div>
            <p className="text-xs text-muted-foreground">
              Reminders are opt-in. By enabling email reminders, you consent to receive supportive
              nudges at your configured times. You can disable either at any time.
            </p>
            <div>
              <label className="text-sm font-medium">Reminder times (your timezone)</label>
              <p className="text-xs text-muted-foreground mb-1">
                e.g. 09:00, 14:00. We send at these times in your timezone.
              </p>
              <input
                type="text"
                className="rounded border px-2 py-1 w-full max-w-xs"
                placeholder="09:00, 14:00"
                value={(settings.reminder_times ?? []).join(', ')}
                onChange={(e) => {
                  const raw = e.target.value.split(',').map((t) => t.trim());
                  const times = raw
                    .map((t) => {
                      const m = t.match(/^(\d{1,2}):(\d{2})$/);
                      return m ? `${m[1].padStart(2, '0')}:${m[2]}` : null;
                    })
                    .filter((t): t is string => t !== null);
                  updateSettings({ reminder_times: times.length ? times : null });
                }}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Timezone</label>
              <select
                className="rounded border px-2 py-1 mt-1 w-full max-w-xs"
                value={settings.timezone ?? 'UTC'}
                onChange={(e) => updateSettings({ timezone: e.target.value || null })}
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern</option>
                <option value="America/Chicago">Central</option>
                <option value="America/Denver">Mountain</option>
                <option value="America/Los_Angeles">Pacific</option>
                <option value="Europe/London">London</option>
                <option value="Europe/Paris">Paris</option>
                <option value="Asia/Tokyo">Tokyo</option>
                <option value="Australia/Sydney">Sydney</option>
              </select>
            </div>
            <div className="flex gap-4">
              <div>
                <label className="text-sm font-medium">Quiet hours start</label>
                <input
                  type="time"
                  className="rounded border px-2 py-1 mt-1 block"
                  value={settings.quiet_hours_start ?? ''}
                  onChange={(e) => updateSettings({ quiet_hours_start: e.target.value || null })}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Quiet hours end</label>
                <input
                  type="time"
                  className="rounded border px-2 py-1 mt-1 block"
                  value={settings.quiet_hours_end ?? ''}
                  onChange={(e) => updateSettings({ quiet_hours_end: e.target.value || null })}
                />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">{REMINDERS_COPY.quietHours}</p>
            <div>
              <label className="text-sm font-medium">{REMINDERS_COPY.reminderCadence}</label>
              <select
                className="rounded border px-2 py-1 mt-1"
                value={settings.reminder_cadence ?? 'daily'}
                onChange={(e) => updateSettings({ reminder_cadence: e.target.value })}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="both">Both</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">{REMINDERS_COPY.reminderTypes}</label>
              <p className="text-xs text-muted-foreground mb-2">{REMINDERS_COPY.reminderTypesHint}</p>
              <div className="flex flex-wrap gap-3">
                {[
                  { id: 'daily_reminder', label: 'Daily goal' },
                  { id: 'weekly_reminder', label: 'Weekly check-in' },
                  { id: 'milestone_reminder', label: 'Milestone ahead' },
                  { id: 'streak_reminder', label: 'Streak reminder' },
                  { id: 'overdue_nudge', label: 'Gentle catch-up reminder' },
                  { id: 'finish_date_risk', label: 'Finish date risk' },
                  { id: 'resume_reminder', label: 'Resume writing' },
                  { id: 'section_reminder', label: 'You were working on this' },
                  { id: 'chapter_target_reminder', label: 'Chapter target' },
                  { id: 'stuck_nudge', label: 'Ready when you are' },
                  { id: 'missed_goal_recovery', label: 'Recovery plan nudges' },
                ].map(({ id, label }) => {
                  const types = settings.reminder_types ?? [
                    'daily_reminder', 'weekly_reminder', 'milestone_reminder', 'streak_reminder',
                    'overdue_nudge', 'finish_date_risk', 'resume_reminder', 'section_reminder',
                    'chapter_target_reminder', 'stuck_nudge', 'missed_goal_recovery',
                  ];
                  const checked = types.includes(id);
                  return (
                    <label key={id} className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() => {
                          const next = checked
                            ? types.filter((t) => t !== id)
                            : [...types, id];
                          updateSettings({ reminder_types: next.length ? next : null });
                        }}
                      />
                      {label}
                    </label>
                  );
                })}
              </div>
            </div>
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={sendTestNotification}
                disabled={testingNotification || !settings.reminder_enabled}
              >
                {testingNotification ? 'Sending...' : REMINDERS_COPY.sendTest}
              </Button>
              <p className="text-xs text-muted-foreground mt-1">{REMINDERS_COPY.sendTestHint}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-medium">Goal presets</p>
              <div className="flex flex-wrap gap-2">
                {(['gentle', 'balanced', 'structured'] as const).map((key) => {
                  const p = GOALS_COPY.presets[key];
                  const active =
                    settings.daily_word_goal === p.daily &&
                    settings.weekly_word_goal === p.weekly;
                  return (
                    <Button
                      key={key}
                      variant={active ? 'default' : 'outline'}
                      size="sm"
                      onClick={() =>
                        updateSettings({
                          daily_word_goal: p.daily,
                          weekly_word_goal: p.weekly,
                        })
                      }
                    >
                      {p.label} ({p.daily}/day)
                    </Button>
                  );
                })}
              </div>
            </div>
            <div className="flex gap-2">
              <label className="text-sm">Daily goal (words)</label>
              <input
                type="number"
                className="rounded border px-2 py-1 w-24"
                value={settings.daily_word_goal ?? ''}
                placeholder="500"
                onChange={(e) => {
                  const v = e.target.value ? parseInt(e.target.value, 10) : null;
                  if (v === null || (!isNaN(v) && v >= 0)) {
                    updateSettings({ daily_word_goal: v });
                  }
                }}
              />
            </div>
            <div className="flex gap-2">
              <label className="text-sm">Weekly goal (words)</label>
              <input
                type="number"
                className="rounded border px-2 py-1 w-24"
                value={settings.weekly_word_goal ?? ''}
                placeholder="3500"
                onChange={(e) => {
                  const v = e.target.value ? parseInt(e.target.value, 10) : null;
                  if (v === null || (!isNaN(v) && v >= 0)) {
                    updateSettings({ weekly_word_goal: v });
                  }
                }}
              />
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={settings.plan_paused ? 'default' : 'outline'}
                size="sm"
                onClick={() => updateSettings({ plan_paused: !settings.plan_paused })}
              >
                {settings.plan_paused ? REMINDERS_COPY.resumePlan : REMINDERS_COPY.pausePlan}
              </Button>
              {settings.plan_paused && (
                <span className="text-sm text-muted-foreground">{REMINDERS_COPY.remindersPaused}</span>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <HowThisWorks
        title={ACCOUNTABILITY_PAGE.howThisWorksTitle}
        summary={ACCOUNTABILITY_PAGE.howThisWorksSummary}
        articleId="accountability-overview"
      >
        <p>{GOALS_COPY.setPace} We count words from your manuscript (notes and outlines don&apos;t count).</p>
        <p>{GOALS_COPY.smallSessionsCount} Choose your style: Gentle (soft nudges), Balanced (supportive check-ins), or Structured (clear expectations). We send recovery nudges when you&apos;ve been away—ready when you are.</p>
      </HowThisWorks>

      {overview && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Card variant="sanctuary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Today</p>
                <Zap className="h-4 w-4 text-primary" />
              </div>
              <p className="text-2xl font-bold">{overview.words_today.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">
                {overview.daily_goal
                  ? GOALS_COPY.ofGoal(overview.daily_goal)
                  : GOALS_COPY.setDailyGoal}
              </p>
              {overview.daily_goal && overview.daily_goal > 0 && (
                <Progress
                  value={Math.min(100, (overview.words_today / overview.daily_goal) * 100)}
                  size="sm"
                  className="mt-2"
                />
              )}
            </CardContent>
          </Card>
          <Card variant="sanctuary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">This week</p>
                <Calendar className="h-4 w-4 text-primary" />
              </div>
              <p className="text-2xl font-bold">{overview.words_this_week.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">
                {overview.weekly_goal
                  ? GOALS_COPY.ofGoal(overview.weekly_goal)
                  : GOALS_COPY.setWeeklyGoal}
              </p>
              {overview.weekly_goal && overview.weekly_goal > 0 && (
                <Progress
                  value={Math.min(100, (overview.words_this_week / overview.weekly_goal) * 100)}
                  size="sm"
                  className="mt-2"
                />
              )}
            </CardContent>
          </Card>
          <Card variant="sanctuary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Consistency</p>
              </div>
              <p className="text-2xl font-bold">{overview.consistency_score}%</p>
              <p className="text-xs text-muted-foreground">Last 4 weeks</p>
            </CardContent>
          </Card>
          <Card variant="sanctuary">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <p className="text-sm text-muted-foreground">Streak</p>
              </div>
              <p className="text-2xl font-bold">{STREAK_COPY.daysOfWriting(overview.current_streak)}</p>
              <p className="text-xs text-muted-foreground">{STREAK_COPY.keepGoing}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {overview?.next_action && (
        <Card variant="soft">
          <CardContent className="flex items-start gap-4 pt-6">
            <BookOpen className="h-8 w-8 text-primary shrink-0" />
            <div>
              <h3 className="font-semibold">{ACCOUNTABILITY_PAGE.suggestedNextStep}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{overview.next_action}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {recoveryPlans.length > 0 && (
        <Card variant="sanctuary">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RotateCcw className="h-5 w-5" />
              Recovery plans
            </CardTitle>
            <CardDescription>
              Life happens. Here are gentle plans to help you get back on track—no judgment.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {recoveryPlans.map((rp) => (
              <div
                key={rp.id}
                className="rounded-lg border bg-muted/30 p-4 space-y-2"
              >
                {rp.message && <p className="text-sm">{rp.message}</p>}
                {rp.suggested_daily_words && (
                  <p className="text-sm font-medium">
                    {RECOVERY_COPY.suggestedWordsPerDay(rp.suggested_daily_words)}
                  </p>
                )}
                {rp.suggested_schedule && rp.suggested_schedule.length > 0 && (
                  <div className="text-xs text-muted-foreground">
                    {rp.suggested_schedule.slice(0, 5).map((s) => (
                      <span key={s.date} className="mr-2">
                        {s.date}: {s.target}w
                      </span>
                    ))}
                  </div>
                )}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => acknowledgeRecovery(rp.id)}
                >
                  {RECOVERY_COPY.gotIt}
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card variant="sanctuary">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Goals
          </CardTitle>
          <CardDescription>
            Word count goals and deadlines. We&apos;ll gently remind you—no guilt, just support.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {goals.length === 0 ? (
            <EmptyState
              icon={<Target className="h-6 w-6" />}
              title={getEmptyStateConfig('no_goals')!.title}
              description={getEmptyStateConfig('no_goals')!.description}
              action={{ label: 'Set goal', href: '/dashboard' }}
            />
          ) : (
            <div className="space-y-4">
              {goals.map((g) => (
                <div
                  key={g.id}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div className="flex items-center gap-4">
                    {g.completed_at ? (
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-success/20 text-success">
                        <Check className="h-5 w-5" />
                      </div>
                    ) : (
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                        <Target className="h-5 w-5" />
                      </div>
                    )}
                    <div>
                      <p className="font-medium">
                        {g.target_words.toLocaleString()} words
                        {g.deadline && (
                          <span className="ml-2 text-sm text-muted-foreground">
                            by {new Date(g.deadline).toLocaleDateString()}
                          </span>
                        )}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {g.completed_at ? 'Completed!' : 'In progress'}
                      </p>
                    </div>
                  </div>
                  {g.completed_at && (
                    <span className="text-sm text-success font-medium">Done</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card variant="soft">
        <CardContent className="flex items-start gap-4 pt-6">
          <Bell className="h-8 w-8 text-primary shrink-0" />
          <div>
            <h3 className="font-semibold">Smart reminders</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              We adapt to your writing patterns. Miss a day? No problem. We&apos;ll suggest
              recovery plans and help you resume where you left off. Pause anytime in settings.
              Check the bell icon in the sidebar for in-app notifications.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
