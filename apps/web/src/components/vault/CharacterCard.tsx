'use client';

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CharacterCardProps {
  character: Record<string, unknown>;
  projectId: string;
  onRefresh: () => void;
}

export function CharacterCard({ character }: CharacterCardProps) {
  const name = String(character.full_name ?? '');
  const role = String(character.role_in_story ?? '');
  const status = String(character.status ?? 'active');
  const excerpt =
    (character.appearance_notes as string)?.slice(0, 80) ||
    (character.backstory as string)?.slice(0, 80) ||
    (character.goals as string)?.slice(0, 80) ||
    '';

  return (
    <Card variant="sanctuary" className="p-4 transition-all hover:shadow-md cursor-pointer group">
      <div className="flex items-start gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Users className="h-5 w-5" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-foreground">{name}</h4>
          {role && (
            <p className="text-sm text-muted-foreground mt-0.5">{role}</p>
          )}
          {excerpt && (
            <p className="text-sm text-muted-foreground mt-2 line-clamp-2">{excerpt}…</p>
          )}
          <div className="flex gap-1.5 mt-3">
            <Badge variant="soft" className="text-xs capitalize">
              {status}
            </Badge>
          </div>
        </div>
      </div>
    </Card>
  );
}
