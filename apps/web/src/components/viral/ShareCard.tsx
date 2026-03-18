'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Flame, Trophy, BookOpen, Zap } from 'lucide-react';

export interface ShareCardData {
  title: string;
  subtitle: string;
  shareType: 'progress' | 'milestone' | 'achievement' | 'book_finished';
  productName?: string;
}

interface ShareCardProps {
  data: ShareCardData;
  displayName?: string;
  className?: string;
  /** Ref for capture (download image) */
  ref?: React.Ref<HTMLDivElement>;
}

const icons: Record<string, React.ComponentType<{ className?: string }>> = {
  progress: Flame,
  milestone: Trophy,
  achievement: Zap,
  book_finished: BookOpen,
};

export const ShareCard = React.forwardRef<HTMLDivElement, ShareCardProps>(
  ({ data, className }, ref) => {
    const Icon = icons[data.shareType] ?? Trophy;
    const product = data.productName ?? 'AUTHORA';

    return (
      <div
        ref={ref}
        className={cn(
          'relative flex flex-col justify-between rounded-2xl border-2 border-border/60 bg-card p-8 shadow-xl',
          'w-full max-w-[400px] min-h-[280px]',
          'text-foreground',
          className
        )}
        style={{ fontFamily: 'var(--font-inter), system-ui, sans-serif' }}
      >
        <div className="flex items-start gap-4">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-primary/15 text-primary">
            <Icon className="h-7 w-7" />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium uppercase tracking-wider text-primary">
              {data.title}
            </p>
            <p className="mt-2 text-xl font-semibold leading-tight text-foreground">
              {data.subtitle}
            </p>
          </div>
        </div>
        <div className="mt-8 flex items-center justify-between border-t border-border/60 pt-6">
          <span className="text-sm font-medium text-muted-foreground">
            {product}
          </span>
          <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
            AI-Powered Book Builder
          </span>
        </div>
      </div>
    );
  }
);
ShareCard.displayName = 'ShareCard';
