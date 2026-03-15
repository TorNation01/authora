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

const STYLES = [
  { value: 'gentle', label: 'Gentle', desc: 'Soft nudges, no pressure' },
  { value: 'balanced', label: 'Balanced', desc: 'Supportive but clear' },
  { value: 'firm', label: 'Firm', desc: 'Clear expectations' },
  { value: 'coach', label: 'Coach-like', desc: 'Motivating and strategic' },
  { value: 'structured', label: 'Highly structured', desc: 'Schedules and milestones' },
];

export default function AccountabilityPage() {
  const { toast } = useToast();
  const [goals, setGoals] = useState<Goal[]>([]);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [settings, setSettings] = useState<AccountabilitySettings | null>(null);
  const [recoveryPlans, setRecoveryPlans] = useState<RecoveryPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

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
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-4xl space-y-8">
      <div className="flex items-start justify-between">
        <PageHeader
          title="Accountability"
          description="Goals that support you—never punish. We adapt to your patterns and help you finish."
          actions={
            <div className="flex items-center gap-2">
              <HelpIcon
                content="Set daily or weekly word goals. We'll nudge you gently (or firmly) based on your preference."
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
            <CardTitle>Reminder & style</CardTitle>
            <CardDescription>
              Choose how AUTHORA supports you. Your style affects reminder tone and recovery plans.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium">Accountability style</label>
              <div className="mt-2 flex flex-wrap gap-2">
                {STYLES.map((s) => (
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
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={settings.reminder_enabled}
                  onChange={(e) => updateSettings({ reminder_enabled: e.target.checked })}
                />
                Enable reminders
              </label>
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
                {settings.plan_paused ? 'Resume plan' : 'Pause plan'}
              </Button>
              {settings.plan_paused && (
                <span className="text-sm text-muted-foreground">Reminders paused</span>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      <HowThisWorks
        title="How accountability works"
        summary="Set goals, get nudges, and track progress. We adapt to your patterns—no guilt."
        articleId="accountability-overview"
      >
        <p>Set daily or weekly word goals in settings. We count words from your manuscript (notes and outlines don&apos;t count).</p>
        <p>Choose your style: Gentle (soft nudges), Balanced (supportive check-ins), or Structured (clear expectations). We send recovery nudges when you&apos;ve been away—ready when you are.</p>
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
                  ? `of ${overview.daily_goal} goal`
                  : 'Set a daily goal in settings'}
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
                  ? `of ${overview.weekly_goal} goal`
                  : 'Set a weekly goal in settings'}
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
              <p className="text-2xl font-bold">{overview.current_streak} days</p>
              <p className="text-xs text-muted-foreground">Keep going!</p>
            </CardContent>
          </Card>
        </div>
      )}

      {overview?.next_action && (
        <Card variant="soft">
          <CardContent className="flex items-start gap-4 pt-6">
            <BookOpen className="h-8 w-8 text-primary shrink-0" />
            <div>
              <h3 className="font-semibold">Next best action</h3>
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
              You missed some goals. Here are supportive plans to get back on track.
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
                    Suggested: {rp.suggested_daily_words} words/day
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
                  Got it
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
              title="No goals yet"
              description="Set a word count goal or deadline. We'll gently remind you—no guilt, just support."
              action={{ label: 'Set a goal', href: '/dashboard' }}
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
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
