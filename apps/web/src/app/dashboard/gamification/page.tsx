'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { PageHeader } from '@/components/layout/PageHeader';
import { Progress } from '@/components/ui/progress';
import { Trophy, Flame, Star, Target, ListTodo, Zap } from 'lucide-react';
import { api } from '@/lib/api';
import { JourneyMap } from '@/components/gamification/JourneyMap';

interface Stats {
  total_words: number;
  current_streak: number;
  longest_streak: number;
  xp: number;
  level: number;
  best_daily_words?: number;
  best_weekly_words?: number;
  next_milestone?: number;
  milestone_progress?: [number, number];
}

interface Quest {
  id: string;
  title: string;
  target_value: number;
  current_value: number;
  xp_reward: number;
  completed_at: string | null;
}

interface JourneyMapData {
  phases: { phase: string; label: string; completed: boolean; current: boolean; progress: number }[];
  current_phase_index: number;
  overall_progress: number;
}

export default function GamificationPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [dailyQuests, setDailyQuests] = useState<Quest[]>([]);
  const [weeklyMissions, setWeeklyMissions] = useState<Quest[]>([]);
  const [journeyMap, setJourneyMap] = useState<JourneyMapData | null>(null);

  useEffect(() => {
    Promise.all([
      api<Stats>('/api/v1/gamification/stats').catch(() => null),
      api<Quest[]>('/api/v1/gamification/quests/daily').catch(() => []),
      api<Quest[]>('/api/v1/gamification/quests/weekly').catch(() => []),
      api<JourneyMapData>('/api/v1/gamification/journey-map').catch(() => null),
    ]).then(([s, dq, wm, jm]) => {
      setStats(s ?? null);
      setDailyQuests(dq ?? []);
      setWeeklyMissions(wm ?? []);
      setJourneyMap(jm ?? null);
    });
  }, []);

  const levelProgress = stats ? ((stats.xp % 1000) / 1000) * 100 : 0;
  const milestonePct =
    stats?.milestone_progress && stats.next_milestone
      ? (stats.milestone_progress[0] / stats.milestone_progress[1]) * 100
      : 0;

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Celebrations"
        description="Celebrate your progress. Every word counts—we're cheering you on."
      />

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Star className="h-6 w-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.level ?? 1}</p>
              <p className="text-sm text-muted-foreground">Level</p>
            </div>
          </div>
          <Progress value={levelProgress} size="sm" className="mt-4" />
        </Card>

        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Flame className="h-6 w-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.current_streak ?? 0}</p>
              <p className="text-sm text-muted-foreground">Day streak</p>
            </div>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Best: {stats?.longest_streak ?? 0} days
          </p>
        </Card>

        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Trophy className="h-6 w-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.total_words?.toLocaleString() ?? 0}</p>
              <p className="text-sm text-muted-foreground">Total words</p>
            </div>
          </div>
        </Card>

        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Target className="h-6 w-6" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats?.xp?.toLocaleString() ?? 0}</p>
              <p className="text-sm text-muted-foreground">XP</p>
            </div>
          </div>
          {stats?.next_milestone && (
            <>
              <p className="mt-2 text-xs text-muted-foreground">
                Next milestone: {stats.next_milestone.toLocaleString()} words
              </p>
              <Progress value={milestonePct} size="sm" className="mt-2" />
            </>
          )}
        </Card>
      </div>

      {(stats?.best_daily_words || stats?.best_weekly_words) && (
        <Card variant="soft" className="mt-6 p-4">
          <p className="text-sm font-medium text-foreground">Personal bests</p>
          <p className="text-sm text-muted-foreground">
            Daily: {(stats.best_daily_words ?? 0).toLocaleString()} words
            {stats.best_weekly_words ? ` · Weekly: ${stats.best_weekly_words.toLocaleString()} words` : ''}
          </p>
        </Card>
      )}

      {journeyMap && (
        <Card variant="sanctuary" className="mt-6 p-6">
          <JourneyMap
            phases={journeyMap.phases}
            currentPhaseIndex={journeyMap.current_phase_index}
            overallProgress={journeyMap.overall_progress}
          />
        </Card>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <ListTodo className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Daily quests</h3>
          </div>
          {dailyQuests.length === 0 ? (
            <p className="text-sm text-muted-foreground">No quests today. Write to earn XP.</p>
          ) : (
            <ul className="space-y-3">
              {dailyQuests.map((q) => (
                <li
                  key={q.id}
                  className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/30 px-3 py-2"
                >
                  <span className={q.completed_at ? 'text-muted-foreground line-through' : ''}>
                    {q.title}
                  </span>
                  <span className="text-sm">
                    {q.current_value}/{q.target_value}
                    {q.completed_at ? ' ✓' : ` · +${q.xp_reward} XP`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card variant="sanctuary" className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Weekly missions</h3>
          </div>
          {weeklyMissions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No missions this week.</p>
          ) : (
            <ul className="space-y-3">
              {weeklyMissions.map((m) => (
                <li
                  key={m.id}
                  className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/30 px-3 py-2"
                >
                  <span className={m.completed_at ? 'text-muted-foreground line-through' : ''}>
                    {m.title}
                  </span>
                  <span className="text-sm">
                    {m.current_value.toLocaleString()}/{m.target_value.toLocaleString()}
                    {m.completed_at ? ' ✓' : ` · +${m.xp_reward} XP`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card variant="soft" className="mt-8 p-6">
        <p className="text-sm text-muted-foreground">
          <strong className="text-foreground">Supportive, not punishing.</strong> Every word you write earns XP.
          Streaks celebrate consistency—but if you miss a day, you can always start fresh. We're here to encourage you.
        </p>
      </Card>
    </div>
  );
}
