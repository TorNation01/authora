'use client';

import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'outline';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium',
        variant === 'default' &&
          'border border-primary/20 bg-primary/5 text-primary/90',
        variant === 'success' &&
          'border border-success/20 bg-success/5 text-success/90',
        variant === 'outline' &&
          'border border-white/20 bg-white/5 text-muted-foreground',
        className
      )}
    >
      {children}
    </span>
  );
}
