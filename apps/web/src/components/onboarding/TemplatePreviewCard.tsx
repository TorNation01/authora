'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api } from '@/lib/api';
import { Loader2, Check, BookOpen } from 'lucide-react';

interface TemplateFull {
  id: string;
  name: string;
  description: string | null;
  who_it_is_for: string | null;
  expected_outcome: string | null;
  suggested_workflow: string | null;
  book_type: string | null;
  genre: string | null;
  default_milestones: unknown[] | null;
  export_recommendations: string[] | null;
}

interface TemplatePreviewCardProps {
  templateId: string | null;
  templateName?: string;
  onActivate?: () => void;
  onStartBlank?: () => void;
}

export function TemplatePreviewCard({
  templateId,
  templateName,
  onActivate,
  onStartBlank,
}: TemplatePreviewCardProps) {
  const [template, setTemplate] = useState<TemplateFull | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!templateId) {
      setTemplate(null);
      return;
    }
    setLoading(true);
    api<TemplateFull>(`/api/v1/templates/${templateId}`)
      .then(setTemplate)
      .catch(() => setTemplate(null))
      .finally(() => setLoading(false));
  }, [templateId]);

  if (!templateId) return null;

  if (loading) {
    return (
      <Card variant="soft" className="mt-4">
        <CardContent className="py-8 flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </CardContent>
      </Card>
    );
  }

  if (!template) return null;

  return (
    <Card variant="soft" className="mt-4 border-primary/20">
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10">
            <BookOpen className="h-4 w-4 text-primary" />
          </div>
          <div>
            <CardTitle className="text-base font-serif">{template.name || templateName}</CardTitle>
            {template.book_type && (
              <Badge variant="soft" className="mt-1 text-xs">
                {template.book_type}
                {template.genre ? ` · ${template.genre}` : ''}
              </Badge>
            )}
          </div>
        </div>
        {template.description && (
          <CardDescription className="text-sm mt-1">{template.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {template.who_it_is_for && (
          <div>
            <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Best for</p>
            <p>{template.who_it_is_for}</p>
          </div>
        )}
        {template.expected_outcome && (
          <div>
            <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">What you get</p>
            <p>{template.expected_outcome}</p>
          </div>
        )}
        {template.suggested_workflow && (
          <div>
            <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Suggested workflow</p>
            <p>{template.suggested_workflow}</p>
          </div>
        )}
        {template.default_milestones && template.default_milestones.length > 0 && (
          <div>
            <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Milestones</p>
            <p className="text-muted-foreground">
              {template.default_milestones.length} milestone{template.default_milestones.length !== 1 ? 's' : ''} included
            </p>
          </div>
        )}
        {template.export_recommendations && template.export_recommendations.length > 0 && (
          <div>
            <p className="font-medium text-muted-foreground text-xs uppercase tracking-wide">Export formats</p>
            <p className="text-muted-foreground">{template.export_recommendations.join(', ')}</p>
          </div>
        )}
        {(onActivate || onStartBlank) && (
          <div className="flex gap-2 pt-2">
            {onActivate && (
              <button
                type="button"
                onClick={onActivate}
                className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
              >
                <Check className="h-4 w-4" />
                Use this template
              </button>
            )}
            {onStartBlank && (
              <button
                type="button"
                onClick={onStartBlank}
                className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-sm font-medium hover:bg-muted/50"
              >
                Start from blank instead
              </button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
