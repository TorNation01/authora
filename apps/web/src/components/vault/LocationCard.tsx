'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MapPin } from 'lucide-react';

interface LocationCardProps {
  location: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

export function LocationCard({ location }: LocationCardProps) {
  const name = String(location.name ?? '');
  const category = String(location.category ?? '');
  const description = (location.description as string)?.slice(0, 100) || '';

  return (
    <Card variant="sanctuary" className="p-4 transition-all hover:shadow-md cursor-pointer group">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <MapPin className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground">{name}</h4>
          <Badge variant="soft" className="text-xs mt-1 capitalize">
            {category.replace(/_/g, ' ')}
          </Badge>
          {description && (
            <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{description}…</p>
          )}
        </div>
      </div>
    </Card>
  );
}
