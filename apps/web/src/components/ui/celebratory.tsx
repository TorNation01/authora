import * as React from 'react';
import { cn } from '@/lib/utils';

interface CelebratoryProps {
  icon?: React.ReactNode;
  title: string;
  message?: string;
  className?: string;
  children?: React.ReactNode;
}

export function Celebratory({ icon, title, message, className, children }: CelebratoryProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-xl border border-primary/20 bg-primary/5 px-8 py-12 text-center animate-fade-in',
        className
      )}
    >
      {icon && (
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/15 text-primary animate-celebrate">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-foreground mb-1">{title}</h3>
      {message && <p className="text-sm text-muted-foreground mb-4 max-w-sm">{message}</p>}
      {children}
    </div>
  );
}
