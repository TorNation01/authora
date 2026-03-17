'use client';

import { cn } from '@/lib/utils';

interface SectionHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  centered?: boolean;
  className?: string;
}

export function SectionHeader({
  eyebrow,
  title,
  description,
  centered = true,
  className,
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        'mx-auto max-w-2xl',
        centered && 'text-center',
        className
      )}
    >
      {eyebrow && (
        <p className="text-sm font-medium uppercase tracking-wider text-primary/80 mb-4">
          {eyebrow}
        </p>
      )}
      <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
        {title}
      </h2>
      {description && (
        <p className="mt-4 text-lg text-muted-foreground leading-relaxed">
          {description}
        </p>
      )}
    </div>
  );
}
