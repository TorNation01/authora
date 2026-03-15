'use client';

import { cn } from '@/lib/utils';
import { Check, Circle } from 'lucide-react';

interface Phase {
  phase: string;
  label: string;
  completed: boolean;
  current: boolean;
  progress: number;
}

interface JourneyMapProps {
  phases: Phase[];
  currentPhaseIndex: number;
  overallProgress: number;
  className?: string;
}

export function JourneyMap({
  phases,
  currentPhaseIndex,
  overallProgress,
  className,
}: JourneyMapProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Book journey</span>
        <span className="font-medium">{Math.round(overallProgress * 100)}%</span>
      </div>
      <div className="relative">
        <div className="flex items-center justify-between gap-1">
          {phases.map((p, i) => (
            <div key={p.phase} className="flex flex-1 flex-col items-center">
              <div
                className={cn(
                  'flex h-8 w-8 items-center justify-center rounded-full border-2 transition-colors',
                  p.completed && 'border-primary bg-primary text-primary-foreground',
                  p.current && !p.completed && 'border-primary bg-primary/10 text-primary',
                  !p.completed && !p.current && 'border-muted-foreground/30 bg-muted/30'
                )}
              >
                {p.completed ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <Circle className={cn('h-3 w-3', p.current && 'fill-primary')} />
                )}
              </div>
              <span
                className={cn(
                  'mt-1.5 text-xs font-medium',
                  p.current ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                {p.label}
              </span>
            </div>
          ))}
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary/80 transition-all duration-500"
            style={{ width: `${overallProgress * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}
