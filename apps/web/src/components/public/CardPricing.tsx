'use client';

import { cn } from '@/lib/utils';

interface CardPricingProps {
  name: string;
  price: string;
  period?: string;
  description?: string;
  features?: string[];
  badge?: string;
  highlighted?: boolean;
  cta: React.ReactNode;
  className?: string;
}

export function CardPricing({
  name,
  price,
  period,
  description,
  features,
  badge,
  highlighted = false,
  cta,
  className,
}: CardPricingProps) {
  return (
    <div
      className={cn(
        'card-premium flex flex-col p-6 sm:p-8',
        highlighted && 'ring-2 ring-primary/30 border-primary/20',
        className
      )}
    >
      {badge && (
        <span className="inline-block w-fit rounded-full bg-primary/20 px-3 py-1 text-xs font-medium text-primary mb-4">
          {badge}
        </span>
      )}
      <h3 className="font-serif text-xl font-semibold text-foreground">{name}</h3>
      <div className="mt-4 flex items-baseline gap-1">
        <span className="text-3xl font-bold text-foreground">{price}</span>
        {period && (
          <span className="text-muted-foreground">{period}</span>
        )}
      </div>
      {description && (
        <p className="mt-2 text-sm text-muted-foreground">{description}</p>
      )}
      {features && features.length > 0 && (
        <ul className="mt-6 flex-1 space-y-3">
          {features.map((f) => (
            <li key={f} className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-primary/50 shrink-0" />
              {f}
            </li>
          ))}
        </ul>
      )}
      <div className="mt-8">{cta}</div>
    </div>
  );
}
