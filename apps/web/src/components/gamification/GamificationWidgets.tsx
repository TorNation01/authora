'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Flame, Star, Trophy, Target } from 'lucide-react';
import { api } from '@/lib/api';

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

export function GamificationWidgets() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api<Stats>('/api/v1/gamification/stats')
      .then(setStats)
      .catch(() => setStats(null));
  }, []);

  if (!stats) return null;

  const totalWords = Number(stats.total_words) || 0;
  const xp = Number(stats.xp) || 0;
  const level = Number(stats.level) || 1;
  const currentStreak = Number(stats.current_streak) || 0;
  const longestStreak = Number(stats.longest_streak) || 0;

  const levelProgress = ((xp % 1000) / 1000) * 100;
  const [m0, m1] = stats.milestone_progress ?? [0, 1];
  const milestonePct = m1 > 0 ? (Number(m0) / Number(m1)) * 100 : 0;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Star className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-lg font-bold">{level}</p>
              <p className="text-xs text-muted-foreground">Level</p>
            </div>
          </div>
          <Progress value={levelProgress} size="sm" className="mt-2" />
        </Card>
      </Link>

      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Flame className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{currentStreak}</p>
              <p className="text-xs text-muted-foreground">Day streak</p>
            </div>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Best: {longestStreak} days</p>
        </Card>
      </Link>

      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Trophy className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{totalWords.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Total words</p>
            </div>
          </div>
          {stats.next_milestone != null && (
            <p className="mt-1 text-xs text-muted-foreground">
              Next: {Number(stats.next_milestone).toLocaleString()}
            </p>
          )}
        </Card>
      </Link>

      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{xp.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">XP</p>
            </div>
          </div>
          {stats.next_milestone && stats.milestone_progress && (
            <Progress value={milestonePct} size="sm" className="mt-2" />
          )}
        </Card>
      </Link>
    </div>
  );
}
