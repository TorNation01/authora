import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/lib/utils';
import { Button } from './button';

export interface EmptyStateAction {
  label: string;
  href?: string;
  onClick?: () => void;
}

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: EmptyStateAction;
  secondaryAction?: EmptyStateAction;
  /** Smart default actions—quick paths shown as subtle links */
  defaultActions?: EmptyStateAction[];
  className?: string;
  children?: React.ReactNode;
}

function ActionButton({ a }: { a: EmptyStateAction }) {
  if (a.href) {
    return (
      <Button asChild size="sm" variant="outline">
        <Link href={a.href}>{a.label}</Link>
      </Button>
    );
  }
  if (a.onClick) {
    return (
      <Button size="sm" variant="outline" onClick={a.onClick}>
        {a.label}
      </Button>
    );
  }
  return null;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  defaultActions,
  className,
  children,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center rounded-xl border border-dashed border-border/50 bg-muted/20 px-8 py-16 text-center',
        className
      )}
    >
      {icon && (
        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-muted/80 text-muted-foreground">
          {icon}
        </div>
      )}
      <h3 className="section-header mb-2">{title}</h3>
      <p className="section-description mb-6 max-w-sm">{description}</p>
      {children}
      {(action || secondaryAction || defaultActions?.length) && (
        <div className="flex flex-col items-center gap-4">
          {(action || secondaryAction) && (
            <div className="flex flex-wrap items-center justify-center gap-3">
              {action && (
                action.href ? (
                  <Button asChild>
                    <Link href={action.href}>{action.label}</Link>
                  </Button>
                ) : (
                  <Button onClick={action.onClick}>{action.label}</Button>
                )
              )}
              {secondaryAction && (
                secondaryAction.href ? (
                  <Button variant="outline" asChild>
                    <Link href={secondaryAction.href}>{secondaryAction.label}</Link>
                  </Button>
                ) : (
                  <Button variant="outline" onClick={secondaryAction.onClick}>
                    {secondaryAction.label}
                  </Button>
                )
              )}
            </div>
          )}
          {defaultActions && defaultActions.length > 0 && (
            <div className="flex flex-wrap items-center justify-center gap-2 text-sm">
              {defaultActions
                .filter((a) => a.href || a.onClick)
                .map((a, i) => (
                  <ActionButton key={i} a={a} />
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
