'use client';

import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CardComparisonProps {
  icon: LucideIcon;
  vs: string;
  authora: string;
  className?: string;
}

export function CardComparison({
  icon: Icon,
  vs,
  authora,
  className,
}: CardComparisonProps) {
  return (
    <div
      className={cn(
        'card-premium flex items-start gap-4 p-6',
        className
      )}
    >
      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/20">
        <Icon className="h-5 w-5 text-primary" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-muted-foreground line-through">{vs}</p>
        <p className="mt-1 font-semibold text-foreground">{authora}</p>
      </div>
    </div>
  );
}
