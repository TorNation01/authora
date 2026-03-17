'use client';

import { cn } from '@/lib/utils';

interface CTABlockProps {
  eyebrow?: string;
  headline: string;
  supporting?: string;
  primary: React.ReactNode;
  secondary?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'accent';
  className?: string;
}

export function CTABlock({
  eyebrow,
  headline,
  supporting,
  primary,
  secondary,
  footer,
  variant = 'default',
  className,
}: CTABlockProps) {
  return (
    <div
      className={cn(
        'relative overflow-hidden py-[var(--section-padding-y)]',
        variant === 'accent' &&
          'bg-gradient-to-b from-transparent via-primary/[0.04] to-transparent',
        className
      )}
    >
      {variant === 'accent' && (
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_70%_50%_at_50%_50%,hsl(var(--primary)/0.06),transparent)]" />
      )}

      <div className="relative mx-auto max-w-4xl px-[var(--section-padding-x)] text-center">
        {eyebrow && (
          <p className="text-sm font-medium uppercase tracking-wider text-primary/80 mb-6">
            {eyebrow}
          </p>
        )}
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl lg:text-5xl">
          {headline}
        </h2>
        {supporting && (
          <p className="mt-6 text-lg text-muted-foreground max-w-2xl mx-auto">
            {supporting}
          </p>
        )}

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          {primary}
          {secondary}
        </div>

        {footer && (
          <p className="mt-6 text-sm text-muted-foreground font-medium">
            {footer}
          </p>
        )}
      </div>
    </div>
  );
}
