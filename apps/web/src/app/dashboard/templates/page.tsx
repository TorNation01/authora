'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
import { BookOpen, Loader2, ChevronRight, Sparkles, Copy, List, Lock, CreditCard, Search, Star } from 'lucide-react';
import Link from 'next/link';
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
  access_level?: string;
  premium_pack_slug?: string | null;
  can_use?: boolean;
  required_action?: string | null;
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

type TemplatePack = {
  slug: string;
  name: string;
  description: string | null;
  price_cents: number;
  template_slugs: string[];
  purchased: boolean;
};

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
  const [marketplaceTemplates, setMarketplaceTemplates] = useState<TemplateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [previewTemplateId, setPreviewTemplateId] = useState<string | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<TemplateFull | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);
  const [packs, setPacks] = useState<TemplatePack[]>([]);

  useEffect(() => {
    api<TemplateCategory[]>('/api/v1/templates/categories')
      .then(setCategories)
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery.trim()) {
      params.set('search', searchQuery.trim());
    } else {
      params.set('featured', 'true');
    }
    api<TemplateSummary[]>(`/api/v1/templates/marketplace?${params}`)
      .then(setMarketplaceTemplates)
      .catch(() => setMarketplaceTemplates([]));
  }, [searchQuery]);

  useEffect(() => {
    api<TemplatePack[]>('/api/v1/templates/packs')
      .then(setPacks)
      .catch(() => setPacks([]));
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

  const featuredTemplates = !searchQuery.trim()
    ? marketplaceTemplates.filter((t) => t.is_featured)
    : [];
  const searchResults = searchQuery.trim() ? marketplaceTemplates : null;

  const handleApplyTemplate = (template: TemplateSummary) => {
    if (template.can_use === false) {
      if (template.required_action === 'upgrade') {
        router.push('/pricing');
        return;
      }
      if (template.required_action?.startsWith('purchase:')) {
        const packSlug = template.required_action.replace('purchase:', '');
        router.push(`/dashboard/billing?pack=${packSlug}`);
        return;
      }
    }
    router.push(`/dashboard/projects/new?templateId=${template.id}`);
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
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
        </div>

        {searchResults !== null && searchQuery.trim() && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Search className="h-5 w-5 text-primary" />
              Search results ({searchResults.length})
            </h2>
            <div className="space-y-3">
              {searchResults.length === 0 ? (
                <p className="text-muted-foreground text-sm">No templates match your search.</p>
              ) : (
                searchResults.map((t) => (
                  <TemplateLibraryCard
                    key={t.id}
                    template={t}
                    onPreview={() => setPreviewTemplateId(t.id)}
                    onApply={() => handleApplyTemplate(t)}
                  />
                ))
              )}
            </div>
          </section>
        )}

        {featuredTemplates.length > 0 && !searchQuery.trim() && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Star className="h-5 w-5 text-primary" />
              Featured templates
            </h2>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {featuredTemplates.slice(0, 6).map((t) => (
                <TemplateLibraryCard
                  key={t.id}
                  template={t}
                  onPreview={() => setPreviewTemplateId(t.id)}
                  onApply={() => handleApplyTemplate(t)}
                />
              ))}
            </div>
          </section>
        )}

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
                        onApply={() => handleApplyTemplate(cat.template)}
                      />
                      {/* Child templates */}
                      {cat.children.map((child) => (
                        <TemplateLibraryCard
                          key={child.id}
                          template={child}
                          onPreview={() => setPreviewTemplateId(child.id)}
                          onApply={() => handleApplyTemplate(child)}
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
                  <div className="flex flex-wrap gap-1.5 mt-1">
                    {(previewTemplate.book_type || previewTemplate.genre) && (
                      <Badge variant="soft" className="text-xs">
                        {[previewTemplate.book_type, previewTemplate.genre].filter(Boolean).join(' · ')}
                      </Badge>
                    )}
                    {previewTemplate.can_use === false && (
                      <Badge variant="outline" className="text-xs border-amber-500/50 text-amber-600 dark:text-amber-400">
                        <Lock className="h-3 w-3 mr-0.5" />
                        Premium
                      </Badge>
                    )}
                  </div>
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
              {previewTemplate.can_use === false && (
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-3 text-sm">
                  <p className="font-medium text-amber-700 dark:text-amber-400">
                    {previewTemplate.required_action === 'upgrade'
                      ? 'Upgrade to Pro or Studio to unlock this template.'
                      : 'Purchase the template pack to unlock this template.'}
                  </p>
                  <p className="text-muted-foreground mt-1 text-xs">
                    {previewTemplate.required_action === 'upgrade'
                      ? 'Pro and Studio plans include access to premium templates.'
                      : 'One-time purchase. Yours forever.'}
                  </p>
                </div>
              )}
              <div className="flex flex-wrap gap-2 pt-4">
                <Button
                  onClick={() => handleApplyTemplate(previewTemplate)}
                  disabled={previewTemplate.can_use === false}
                >
                  {previewTemplate.can_use === false ? (
                    <>
                      <Lock className="h-4 w-4 mr-2" />
                      {previewTemplate.required_action === 'upgrade' ? 'Upgrade to unlock' : 'Purchase to unlock'}
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-4 w-4 mr-2" />
                      Use this template
                    </>
                  )}
                </Button>
                {previewTemplate.can_use === false && previewTemplate.required_action?.startsWith('purchase:') && (
                  <Button variant="outline" asChild>
                    <Link href="/dashboard/billing">
                      <CreditCard className="h-4 w-4 mr-2" />
                      View packs
                    </Link>
                  </Button>
                )}
                {previewTemplate.can_use === false && previewTemplate.required_action === 'upgrade' && (
                  <Button variant="outline" asChild>
                    <Link href="/pricing">
                      <CreditCard className="h-4 w-4 mr-2" />
                      View plans
                    </Link>
                  </Button>
                )}
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
  const isLocked = template.can_use === false;
  return (
    <Card
      variant="soft"
      className={`group transition-all hover:shadow-md hover:border-primary/20 ${isChild ? 'ml-4 border-l-2 border-l-primary/30' : ''} ${isLocked ? 'opacity-95' : ''}`}
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
          {isLocked && (
            <Badge variant="outline" className="text-xs border-amber-500/50 text-amber-600 dark:text-amber-400">
              <Lock className="h-3 w-3 mr-0.5" />
              Premium
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex gap-2">
          <Button size="sm" onClick={() => onApply()} variant={isLocked ? 'outline' : 'default'}>
            {isLocked ? (
              <>
                <Lock className="h-3.5 w-3.5 mr-1.5" />
                {template.required_action === 'upgrade' ? 'Upgrade' : 'Purchase'}
              </>
            ) : (
              'Use template'
            )}
          </Button>
          <Button variant="outline" size="sm" onClick={onPreview}>
            Preview
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
