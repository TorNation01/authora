'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useUser } from '@/contexts/UserContext';
import { BookOpen, Loader2, ChevronRight, Sparkles, Copy, List } from 'lucide-react';
import { CATEGORY_DESCRIPTIONS } from '@/content/template-copy';

type TemplateSummary = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  book_type: string | null;
  genre: string | null;
  category: string;
  is_featured: boolean;
};

type TemplateCategory = {
  category: string;
  name: string;
  slug: string;
  template: TemplateSummary;
  children: TemplateSummary[];
};

type ChapterSkeleton = { title?: string; summary?: string };
type PlanningSection = { id?: string; title?: string; guidance?: string };

type TemplateFull = TemplateSummary & {
  who_it_is_for: string | null;
  expected_outcome: string | null;
  suggested_workflow: string | null;
  default_milestones: unknown[] | null;
  export_recommendations: string[] | null;
  chapter_skeletons: ChapterSkeleton[] | null;
  default_structure?: { planning_sections?: PlanningSection[] } | null;
};

export default function TemplateMarketplacePage() {
  const router = useRouter();
  const { toast } = useToast();
  const user = useUser();
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [previewTemplateId, setPreviewTemplateId] = useState<string | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<TemplateFull | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);

  useEffect(() => {
    api<TemplateCategory[]>('/api/v1/templates/categories')
      .then(setCategories)
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!previewTemplateId) {
      setPreviewTemplate(null);
      return;
    }
    setPreviewLoading(true);
    api<TemplateFull>(`/api/v1/templates/${previewTemplateId}`)
      .then(setPreviewTemplate)
      .catch(() => setPreviewTemplate(null))
      .finally(() => setPreviewLoading(false));
  }, [previewTemplateId]);

  const filteredCategories = activeCategory
    ? categories.filter((c) => c.category === activeCategory)
    : categories;

  const handleApplyTemplate = (templateId: string) => {
    router.push(`/dashboard/projects/new?templateId=${templateId}`);
  };

  async function handleDuplicateTemplate(templateId: string) {
    if (!user?.is_admin) return;
    setDuplicatingId(templateId);
    try {
      const res = await api<{ id: string; slug: string; name: string }>(
        `/api/v1/admin/templates/${templateId}/duplicate`,
        { method: 'POST' }
      );
      toast({ title: 'Template duplicated', description: `Created "${res.name}"` });
      setPreviewTemplateId(null);
      api<TemplateCategory[]>('/api/v1/templates/categories')
        .then(setCategories)
        .catch(() => {});
    } catch {
      toast({ title: 'Failed to duplicate template', variant: 'destructive' });
    } finally {
      setDuplicatingId(null);
    }
  }

  return (
    <div className="min-h-screen">
      <PageHeader
        title="Template library"
        description="Choose a template that matches the kind of book you want to write. Apply one to start a new project with a ready-to-use structure."
      />

      <div className="mx-auto max-w-6xl px-4 py-6">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Category sidebar */}
            <aside className="lg:w-56 shrink-0">
              <nav className="space-y-1">
                <button
                  type="button"
                  onClick={() => setActiveCategory(null)}
                  className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    !activeCategory
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                  }`}
                >
                  All categories
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat.category}
                    type="button"
                    onClick={() => setActiveCategory(cat.category)}
                    className={`w-full flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors text-left ${
                      activeCategory === cat.category
                        ? 'bg-primary/10 text-primary'
                        : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
                    }`}
                  >
                    {cat.name}
                  </button>
                ))}
              </nav>
            </aside>

            {/* Template grid */}
            <div className="flex-1 min-w-0">
              <div className="space-y-10">
                {filteredCategories.map((cat) => (
                  <section key={cat.category}>
                    <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                      <BookOpen className="h-5 w-5 text-primary" />
                      {cat.name}
                    </h2>
                    {CATEGORY_DESCRIPTIONS[cat.category] && (
                      <p className="text-sm text-muted-foreground mb-4">
                        {CATEGORY_DESCRIPTIONS[cat.category]}
                      </p>
                    )}
                    <div className="space-y-3">
                      {/* Parent template */}
                      <TemplateLibraryCard
                        template={cat.template}
                        onPreview={() => setPreviewTemplateId(cat.template.id)}
                        onApply={() => handleApplyTemplate(cat.template.id)}
                      />
                      {/* Child templates */}
                      {cat.children.map((child) => (
                        <TemplateLibraryCard
                          key={child.id}
                          template={child}
                          onPreview={() => setPreviewTemplateId(child.id)}
                          onApply={() => handleApplyTemplate(child.id)}
                          isChild
                        />
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Preview dialog */}
      <Dialog open={!!previewTemplateId} onOpenChange={(o) => !o && setPreviewTemplateId(null)}>
        <DialogContent className="sm:max-w-xl max-h-[85vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Template preview</DialogTitle>
            <DialogDescription>
              Review this template before applying. You can create a new project from it.
            </DialogDescription>
          </DialogHeader>
          {previewLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : previewTemplate ? (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <BookOpen className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold">{previewTemplate.name}</h3>
                  {(previewTemplate.book_type || previewTemplate.genre) && (
                    <Badge variant="soft" className="mt-1 text-xs">
                      {[previewTemplate.book_type, previewTemplate.genre].filter(Boolean).join(' · ')}
                    </Badge>
                  )}
                </div>
              </div>
              {previewTemplate.description && (
                <p className="text-sm text-muted-foreground">{previewTemplate.description}</p>
              )}
              {previewTemplate.who_it_is_for && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Best for</p>
                  <p className="text-sm mt-0.5">{previewTemplate.who_it_is_for}</p>
                </div>
              )}
              {previewTemplate.expected_outcome && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">What you get</p>
                  <p className="text-sm mt-0.5">{previewTemplate.expected_outcome}</p>
                </div>
              )}
              {previewTemplate.suggested_workflow && (
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Suggested workflow</p>
                  <p className="text-sm mt-0.5">{previewTemplate.suggested_workflow}</p>
                </div>
              )}
              {/* Structure preview: planning sections + chapters */}
              {(previewTemplate.default_structure?.planning_sections?.length ||
                (previewTemplate.chapter_skeletons && previewTemplate.chapter_skeletons.length > 0)) && (
                <div className="rounded-lg border bg-muted/30 p-3 space-y-2">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide flex items-center gap-1.5">
                    <List className="h-3.5 w-3.5" />
                    Structure
                  </p>
                  {previewTemplate.default_structure?.planning_sections &&
                    previewTemplate.default_structure.planning_sections.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-muted-foreground mb-1">Planning sections</p>
                        <ul className="text-sm space-y-0.5 text-muted-foreground">
                          {previewTemplate.default_structure.planning_sections
                            .slice(0, 8)
                            .map((s, i) => (
                              <li key={s.id ?? i}>
                                {s.title ?? `Section ${i + 1}`}
                              </li>
                            ))}
                          {previewTemplate.default_structure.planning_sections.length > 8 && (
                            <li className="italic">
                              +{previewTemplate.default_structure.planning_sections.length - 8} more
                            </li>
                          )}
                        </ul>
                      </div>
                    )}
                  {previewTemplate.chapter_skeletons && previewTemplate.chapter_skeletons.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground mb-1">
                        Chapters ({previewTemplate.chapter_skeletons.length})
                      </p>
                      <ul className="text-sm space-y-0.5 text-muted-foreground">
                        {previewTemplate.chapter_skeletons.slice(0, 6).map((ch, i) => (
                          <li key={i}>
                            {ch.title}
                            {ch.summary ? ` — ${ch.summary}` : ''}
                          </li>
                        ))}
                        {previewTemplate.chapter_skeletons.length > 6 && (
                          <li className="italic">
                            +{previewTemplate.chapter_skeletons.length - 6} more
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              <div className="flex flex-wrap gap-2 pt-4">
                <Button onClick={() => handleApplyTemplate(previewTemplate.id)}>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Use this template
                </Button>
                {user?.is_admin && (
                  <Button
                    variant="outline"
                    onClick={() => handleDuplicateTemplate(previewTemplate.id)}
                    disabled={duplicatingId === previewTemplate.id}
                  >
                    {duplicatingId === previewTemplate.id ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Copy className="h-4 w-4 mr-2" />
                    )}
                    Duplicate
                  </Button>
                )}
                <Button variant="outline" onClick={() => setPreviewTemplateId(null)}>
                  Close
                </Button>
              </div>
            </div>
          ) : null}
        </DialogContent>
      </Dialog>
    </div>
  );
}

function TemplateLibraryCard({
  template,
  onPreview,
  onApply,
  isChild = false,
}: {
  template: TemplateSummary;
  onPreview: () => void;
  onApply: () => void;
  isChild?: boolean;
}) {
  return (
    <Card
      variant="soft"
      className={`group transition-all hover:shadow-md hover:border-primary/20 ${isChild ? 'ml-4 border-l-2 border-l-primary/30' : ''}`}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <BookOpen className="h-4 w-4 text-primary" />
            </div>
            <div>
              <CardTitle className="font-serif text-base">{template.name}</CardTitle>
              {template.description && (
                <CardDescription className="text-sm mt-0.5 line-clamp-2">{template.description}</CardDescription>
              )}
            </div>
          </div>
          <ChevronRight className="h-5 w-5 text-muted-foreground shrink-0" />
        </div>
        <div className="flex flex-wrap gap-1.5 mt-2">
          {template.book_type && (
            <Badge variant="soft" className="text-xs">
              {template.book_type}
            </Badge>
          )}
          {template.genre && (
            <Badge variant="outline" className="text-xs">
              {template.genre}
            </Badge>
          )}
          {template.is_featured && (
            <Badge variant="default" className="text-xs">
              Featured
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex gap-2">
          <Button size="sm" onClick={onApply}>
            Use template
          </Button>
          <Button variant="outline" size="sm" onClick={onPreview}>
            Preview
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
