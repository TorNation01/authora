import { cn } from '@/lib/utils';

interface FeaturePageSectionProps {
  children: React.ReactNode;
  className?: string;
  noPadding?: boolean;
}

export function FeaturePageSection({
  children,
  className,
  noPadding,
}: FeaturePageSectionProps) {
  return (
    <section
      className={cn(
        'border-t border-white/[0.06]',
        !noPadding && 'py-[var(--section-padding-y)]',
        className
      )}
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)]">{children}</div>
    </section>
  );
}
