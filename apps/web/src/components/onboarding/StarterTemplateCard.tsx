'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  BookOpen,
  Copy,
  MoreHorizontal,
  Pencil,
  FileQuestion,
} from 'lucide-react';
import type { StarterTemplate } from '@/content/starter-templates';
import { GUIDANCE_LABELS } from '@/content/starter-templates';

interface StarterTemplateCardProps {
  starter: StarterTemplate;
  templateId: string | null;
  onUseStarter: () => void;
  onCustomize: () => void;
  onStartBlank?: () => void;
  /** Whether save-as-template is available (future) */
  canSaveAsTemplate?: boolean;
}

export function StarterTemplateCard({
  starter,
  templateId,
  onUseStarter,
  onCustomize,
  onStartBlank,
  canSaveAsTemplate = false,
}: StarterTemplateCardProps) {
  const isBlank = starter.slug === 'blank';

  return (
    <Card
      variant="sanctuary"
      className="group transition-all hover:shadow-md hover:border-primary/20 flex flex-col"
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <BookOpen className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="font-serif text-base">{starter.name}</CardTitle>
              <CardDescription className="text-sm mt-0.5 line-clamp-2">
                {starter.shortDescription}
              </CardDescription>
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 shrink-0 opacity-60 group-hover:opacity-100">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={onUseStarter}>
                <Copy className="mr-2 h-4 w-4" />
                Use this starter
              </DropdownMenuItem>
              {!isBlank && (
                <DropdownMenuItem onClick={onCustomize}>
                  <Pencil className="mr-2 h-4 w-4" />
                  Customize
                </DropdownMenuItem>
              )}
              {canSaveAsTemplate && (
                <DropdownMenuItem disabled>
                  <FileQuestion className="mr-2 h-4 w-4" />
                  Save as template (coming soon)
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="flex flex-wrap gap-1.5 mt-2">
          <Badge variant="soft" className="text-xs">
            {GUIDANCE_LABELS[starter.guidanceLevel]}
          </Badge>
          {starter.suggestedExports.length > 0 && (
            <Badge variant="outline" className="text-xs">
              {starter.suggestedExports.slice(0, 2).join(', ')}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col gap-3 text-sm">
        <div>
          <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Best for</p>
          <p className="text-muted-foreground">{starter.whoItIsFor}</p>
        </div>
        <div>
          <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Guidance</p>
          <p className="text-muted-foreground">{starter.guidanceDescription}</p>
        </div>
        <div className="mt-auto pt-4 flex flex-wrap gap-2">
          <Button onClick={onUseStarter} size="sm">
            Use this starter
          </Button>
          {!isBlank && (
            <Button variant="outline" size="sm" onClick={onCustomize}>
              Customize
            </Button>
          )}
          {onStartBlank && (
            <Button variant="ghost" size="sm" onClick={onStartBlank} className="text-muted-foreground">
              Start blank instead
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
