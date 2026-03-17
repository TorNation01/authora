'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PublicInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const PublicInput = React.forwardRef<HTMLInputElement, PublicInputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id || React.useId();

    return (
      <div className="space-y-2">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-foreground"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'flex h-11 w-full rounded-md border border-white/[0.12] bg-white/[0.04] px-4 py-2 text-sm text-foreground placeholder:text-muted-foreground',
            'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/30',
            'transition-colors duration-200',
            'disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-destructive/50 focus:ring-destructive/50',
            className
          )}
          {...props}
        />
        {error && (
          <p className="text-sm text-destructive">{error}</p>
        )}
      </div>
    );
  }
);
PublicInput.displayName = 'PublicInput';

export { PublicInput };
