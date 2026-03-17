'use client';

import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CardUseCaseProps {
  icon: LucideIcon;
  title: string;
  copy: string;
  className?: string;
}

export function CardUseCase({ icon: Icon, title, copy, className }: CardUseCaseProps) {
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
      <div>
        <h3 className="font-semibold text-foreground">{title}</h3>
        <p className="mt-1 text-sm text-muted-foreground leading-relaxed">{copy}</p>
      </div>
    </div>
  );
}
