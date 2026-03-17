'use client';

import { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CardFeatureProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  items?: string[];
  className?: string;
}

export function CardFeature({
  icon: Icon,
  title,
  description,
  items,
  className,
}: CardFeatureProps) {
  return (
    <div
      className={cn(
        'card-premium flex flex-col p-6',
        className
      )}
    >
      <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/15 ring-1 ring-primary/20 mb-5">
        <Icon className="h-6 w-6 text-primary" />
      </div>
      <h3 className="font-semibold text-foreground text-lg">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
          {description}
        </p>
      )}
      {items && items.length > 0 && (
        <ul className="mt-4 space-y-2">
          {items.map((item) => (
            <li
              key={item}
              className="text-sm text-muted-foreground flex items-center gap-2"
            >
              <span className="h-1.5 w-1.5 rounded-full bg-primary/50 shrink-0" />
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
