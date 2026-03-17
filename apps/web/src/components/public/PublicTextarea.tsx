'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

export interface PublicTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

const PublicTextarea = React.forwardRef<HTMLTextAreaElement, PublicTextareaProps>(
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
        <textarea
          ref={ref}
          id={inputId}
          className={cn(
            'input-public',
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
PublicTextarea.displayName = 'PublicTextarea';

export { PublicTextarea };
