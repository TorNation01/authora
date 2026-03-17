'use client';

import { cn } from '@/lib/utils';

interface SectionLayoutProps {
  children: React.ReactNode;
  variant?: 'default' | 'muted' | 'accent';
  className?: string;
  id?: string;
}

export function SectionLayout({
  children,
  variant = 'default',
  className,
  id,
}: SectionLayoutProps) {
  return (
    <section
      id={id}
      className={cn(
        'py-[var(--section-padding-y)]',
        variant === 'muted' && 'border-t border-white/[0.06] bg-muted/20',
        variant === 'accent' && 'border-t border-white/[0.06] bg-primary/[0.03]',
        className
      )}
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">
        {children}
      </div>
    </section>
  );
}
