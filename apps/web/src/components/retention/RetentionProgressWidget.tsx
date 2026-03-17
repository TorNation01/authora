'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Target, Calendar, TrendingUp, Zap } from 'lucide-react';
import { api } from '@/lib/api';
import { STREAK_COPY } from '@/content/accountability-copy';

interface Overview {
  daily_goal: number | null;
  weekly_goal: number | null;
  words_today: number;
  words_this_week: number;
  consistency_score: number;
  current_streak: number;
  next_action: string;
}

export function RetentionProgressWidget() {
  const [overview, setOverview] = useState<Overview | null>(null);

  useEffect(() => {
    api<Overview>('/api/v1/accountability/overview')
      .then(setOverview)
      .catch(() => setOverview(null));
  }, []);

  if (!overview) return null;

  const dailyPct = overview.daily_goal && overview.daily_goal > 0
    ? Math.min(100, (overview.words_today / overview.daily_goal) * 100)
    : null;
  const weeklyPct = overview.weekly_goal && overview.weekly_goal > 0
    ? Math.min(100, (overview.words_this_week / overview.weekly_goal) * 100)
    : null;

  return (
    <Link href="/dashboard/accountability">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Zap className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-lg font-bold">{overview.words_today.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">
                {overview.daily_goal
                  ? `of ${overview.daily_goal} today`
                  : 'Words today'}
              </p>
            </div>
          </div>
          {dailyPct != null && <Progress value={dailyPct} size="sm" className="mt-2" />}
        </Card>

        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Calendar className="h-5 w-5" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-lg font-bold">{overview.words_this_week.toLocaleString()}</p>
              <p className="text-xs text-muted-foreground">
                {overview.weekly_goal
                  ? `of ${overview.weekly_goal} this week`
                  : 'Words this week'}
              </p>
            </div>
          </div>
          {weeklyPct != null && <Progress value={weeklyPct} size="sm" className="mt-2" />}
        </Card>

        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{STREAK_COPY.daysOfWriting(overview.current_streak)}</p>
              <p className="text-xs text-muted-foreground">{STREAK_COPY.keepGoing}</p>
            </div>
          </div>
        </Card>

        <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Target className="h-5 w-5" />
            </div>
            <div>
              <p className="text-lg font-bold">{overview.consistency_score}%</p>
              <p className="text-xs text-muted-foreground">Consistency (4 weeks)</p>
            </div>
          </div>
        </Card>
      </div>
    </Link>
  );
}
