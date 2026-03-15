'use client';

import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';
import { Trophy, Flame, BookOpen, Zap, Sunrise } from 'lucide-react';

export type CelebrationEvent =
  | { type: 'badge'; badge_id: string; name: string; xp: number }
  | { type: 'milestone'; words: number; xp: number }
  | { type: 'chapter_complete'; chapter_id: string; xp: number }
  | { type: 'comeback'; xp: number; days_away: number }
  | { type: 'daily_quest'; title: string; xp: number }
  | { type: 'weekly_mission'; title: string; xp: number }
  | { type: 'focus_session'; xp: number; minutes: number }
  | { type: 'personal_best_daily'; words: number }
  | { type: 'personal_best_weekly'; words: number };

interface CelebrationToastProps {
  event: CelebrationEvent;
  onDismiss?: () => void;
  className?: string;
}

const icons: Record<string, React.ComponentType<{ className?: string }>> = {
  badge: Trophy,
  milestone: Trophy,
  chapter_complete: BookOpen,
  comeback: Sunrise,
  daily_quest: Zap,
  weekly_mission: Zap,
  focus_session: Zap,
  personal_best_daily: Flame,
  personal_best_weekly: Flame,
};

function getMessage(event: CelebrationEvent): string {
  switch (event.type) {
    case 'badge':
      return `${event.name} — +${event.xp} XP`;
    case 'milestone':
      return `${event.words.toLocaleString()} words — +${event.xp} XP`;
    case 'chapter_complete':
      return `Chapter complete — +${event.xp} XP`;
    case 'comeback':
      return `Welcome back — +${event.xp} XP`;
    case 'daily_quest':
      return `${event.title} — +${event.xp} XP`;
    case 'weekly_mission':
      return `${event.title} — +${event.xp} XP`;
    case 'focus_session':
      return `Focus session — +${event.xp} XP`;
    case 'personal_best_daily':
      return `Daily best: ${event.words.toLocaleString()} words`;
    case 'personal_best_weekly':
      return `Weekly best: ${event.words.toLocaleString()} words`;
    default:
      return 'Achievement unlocked!';
  }
}

export function CelebrationToast({ event, onDismiss, className }: CelebrationToastProps) {
  const [visible, setVisible] = useState(true);
  const Icon = icons[event.type] ?? Trophy;

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false);
      onDismiss?.();
    }, 4000);
    return () => clearTimeout(t);
  }, [onDismiss]);

  if (!visible) return null;

  return (
    <div
      className={cn(
        'flex items-center gap-3 rounded-lg border border-primary/20 bg-card/95 px-4 py-3 shadow-lg backdrop-blur-sm animate-in fade-in slide-in-from-top-2 duration-300',
        className
      )}
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/15 text-primary">
        <Icon className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-foreground">{getMessage(event)}</p>
      </div>
    </div>
  );
}
