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

  const levelProgress = ((stats.xp % 1000) / 1000) * 100;
  const milestonePct = stats.milestone_progress
    ? (stats.milestone_progress[0] / stats.milestone_progress[1]) * 100
    : 0;

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Star className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-lg font-bold">{stats.level}</p>
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
              <p className="text-lg font-bold">{stats.current_streak}</p>
              <p className="text-xs text-muted-foreground">Day streak</p>
            </div>
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Best: {stats.longest_streak} days</p>
        </Card>
      </Link>

      <Link href="/dashboard/gamification">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Trophy className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{stats.total_words.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">Total words</p>
            </div>
          </div>
          {stats.next_milestone && (
            <p className="mt-1 text-xs text-muted-foreground">
              Next: {stats.next_milestone.toLocaleString()}
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
              <p className="text-lg font-bold">{stats.xp.toLocaleString()}</p>
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
