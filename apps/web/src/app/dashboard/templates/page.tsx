'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
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
import { createTemplateCheckout } from '@/lib/billing';
import { useToast } from '@/hooks/use-toast';
import { useUser } from '@/contexts/UserContext';
import { BookOpen, Loader2, ChevronRight, Sparkles, Copy, List, Lock, CreditCard, Search, Star, Users, Filter, TrendingUp, Award, LayoutTemplate } from 'lucide-react';
import Link from 'next/link';
import { EmptyState } from '@/components/ui/empty-state';
import { CATEGORY_DESCRIPTIONS } from '@/content/template-copy';

type TemplateSummary = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  book_type: string | null;
  genre: string | null;
  category: string;
  parent_id?: string | null;
  sort_order?: number;
  is_featured: boolean;
  access_level?: string;
  premium_pack_slug?: string | null;
  price_cents?: number | null;
  is_paid?: boolean;
  can_use?: boolean;
  required_action?: string | null;
  creator_name?: string | null;
  usage_count?: number;
  rating_avg?: number | null;
  rating_count?: number;
};

type TemplateCategory = {
  category: string;
  name: string;
  slug: string;
  template: TemplateSummary;
  children: TemplateSummary[];
};

type TemplateWithParent = TemplateSummary & { parent_id?: string | null };

function buildCategoriesFromFlat(flat: TemplateWithParent[]): TemplateCategory[] {
  const parents = flat.filter((t) => !t.parent_id || t.parent_id === null);
  const byParentId = flat.reduce<Record<string, TemplateSummary[]>>((acc, t) => {
    if (t.parent_id) {
      const pid = String(t.parent_id);
      if (!acc[pid]) acc[pid] = [];
      acc[pid].push(t);
    }
    return acc;
  }, {});
  if (parents.length === 0 && flat.length > 0) {
    return [
      {
        category: 'all',
        name: 'All templates',
        slug: 'all',
        template: flat[0] as TemplateSummary,
        children: flat.slice(1),
      },
    ];
  }
  return parents
    .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
    .map((p) => {
      const id = typeof p.id === 'string' ? p.id : String(p.id);
      const children = (byParentId[id] ?? []).sort(
        (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0)
      );
      return {
        category: p.category ?? p.slug ?? id,
        name: p.name,
        slug: p.slug,
        template: p,
        children,
      };
    });
}

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
  creator_name?: string | null;
  usage_count?: number;
  rating_avg?: number | null;
  rating_count?: number;
};

export default function TemplateMarketplacePage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();
  const user = useUser();
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [marketplaceTemplates, setMarketplaceTemplates] = useState<TemplateSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterBookType, setFilterBookType] = useState<string>('');
  const [filterGenre, setFilterGenre] = useState<string>('');
  const [filterPriceMin, setFilterPriceMin] = useState<string>('');
  const [filterPriceMax, setFilterPriceMax] = useState<string>('');
  const [previewTemplateId, setPreviewTemplateId] = useState<string | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<TemplateFull | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [duplicatingId, setDuplicatingId] = useState<string | null>(null);
  const [packs, setPacks] = useState<TemplatePack[]>([]);
  const [purchasedTemplates, setPurchasedTemplates] = useState<TemplateSummary[]>([]);
  const [purchasingTemplateId, setPurchasingTemplateId] = useState<string | null>(null);
  const [featuredCreators, setFeaturedCreators] = useState<{ creator_id: string; display_name: string }[]>([]);
  const [trendingTemplates, setTrendingTemplates] = useState<
    { template_id: string; slug: string; name: string; creator_name: string | null; activity_count: number }[]
  >([]);
  const [topSellers, setTopSellers] = useState<
    { template_id: string; slug: string; name: string; creator_name: string | null; sales: number; revenue_cents: number }[]
  >([]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await api<TemplateCategory[]>('/api/v1/templates/categories');
        if (Array.isArray(cats) && cats.length > 0) {
          setCategories(cats);
          setLoading(false);
          return;
        }
      } catch {
        /* fall through to /all */
      }
      try {
        const all = await api<TemplateSummary[]>('/api/v1/templates/all');
        const flat = Array.isArray(all) ? all : [];
        const built = buildCategoriesFromFlat(flat);
        setCategories(built);
      } catch {
        setCategories([]);
      } finally {
        setLoading(false);
      }
    };
    loadCategories();
  }, []);

  useEffect(() => {
    const loadMarketplace = async () => {
      const params = new URLSearchParams();
      const hasFilters = filterBookType || filterGenre || filterPriceMin || filterPriceMax;
      if (searchQuery.trim()) {
        params.set('search', searchQuery.trim());
      } else if (!hasFilters) {
        params.set('featured', 'true');
      }
      if (filterBookType) params.set('book_type', filterBookType);
      if (filterGenre) params.set('genre', filterGenre);
      const minCents = filterPriceMin ? Math.round(parseFloat(filterPriceMin) * 100) : null;
      const maxCents = filterPriceMax ? Math.round(parseFloat(filterPriceMax) * 100) : null;
      if (minCents != null && !isNaN(minCents)) params.set('price_min', String(minCents));
      if (maxCents != null && !isNaN(maxCents)) params.set('price_max', String(maxCents));
      try {
        const data = await api<TemplateSummary[]>(`/api/v1/templates/marketplace?${params}`);
        if (Array.isArray(data) && data.length > 0) {
          setMarketplaceTemplates(data);
          return;
        }
      } catch {
        /* fall through */
      }
      if (!hasFilters && !searchQuery.trim()) {
        try {
          const all = await api<TemplateSummary[]>('/api/v1/templates/all');
          const flat = Array.isArray(all) ? all : [];
          setMarketplaceTemplates(flat.filter((t) => t.is_featured).length > 0 ? flat.filter((t) => t.is_featured) : flat.slice(0, 12));
        } catch {
          setMarketplaceTemplates([]);
        }
      } else {
        setMarketplaceTemplates([]);
      }
    };
    loadMarketplace();
  }, [searchQuery, filterBookType, filterGenre, filterPriceMin, filterPriceMax]);

  useEffect(() => {
    api<TemplatePack[]>('/api/v1/templates/packs')
      .then(setPacks)
      .catch(() => setPacks([]));
  }, []);

  useEffect(() => {
    api<TemplateSummary[]>('/api/v1/templates/purchased')
      .then(setPurchasedTemplates)
      .catch(() => setPurchasedTemplates([]));
  }, []);

  useEffect(() => {
    api<{ creator_id: string; display_name: string }[]>('/api/v1/growth/featured-creators')
      .then(setFeaturedCreators)
      .catch(() => setFeaturedCreators([]));
  }, []);

  useEffect(() => {
    api<{ template_id: string; slug: string; name: string; creator_name: string | null; activity_count: number }[]>(
      '/api/v1/templates/trending'
    )
      .then(setTrendingTemplates)
      .catch(() => setTrendingTemplates([]));
  }, []);

  useEffect(() => {
    api<
      { template_id: string; slug: string; name: string; creator_name: string | null; sales: number; revenue_cents: number }[]
    >('/api/v1/templates/top-sellers')
      .then(setTopSellers)
      .catch(() => setTopSellers([]));
  }, []);

  useEffect(() => {
    const purchased = searchParams.get('template_purchased');
    if (purchased === '1') {
      toast({ title: 'Template purchased successfully' });
      api<TemplateSummary[]>('/api/v1/templates/purchased')
        .then(setPurchasedTemplates)
        .catch(() => {});
      router.replace('/dashboard/templates');
    }
  }, [searchParams, toast, router]);

  useEffect(() => {
    if (!previewTemplateId) {
      setPreviewTemplate(null);
      return;
    }
    setPreviewLoading(true);
    api<TemplateFull>(`/api/v1/templates/${previewTemplateId}`)
      .then((t) => {
        setPreviewTemplate(t);
        api(`/api/v1/templates/${previewTemplateId}/view`, { method: 'POST' }).catch(() => {});
      })
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
      if (template.required_action?.startsWith('purchase_template:')) {
        setPreviewTemplateId(template.id);
        return;
      }
    }
    router.push(`/dashboard/projects/new?templateId=${template.id}`);
  };

  const handlePurchaseTemplate = async (templateId: string) => {
    setPurchasingTemplateId(templateId);
    try {
      const result = await createTemplateCheckout(templateId, {
        successUrl: `${window.location.origin}/dashboard/templates?template_purchased=1`,
        cancelUrl: window.location.href,
      });
      if (result?.url) {
        window.location.href = result.url;
      } else {
        toast({ title: 'Checkout not available', variant: 'destructive' });
      }
    } catch {
      toast({ title: 'Failed to start checkout', variant: 'destructive' });
    } finally {
      setPurchasingTemplateId(null);
    }
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

      <div className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8">
        {featuredCreators.length > 0 && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Users className="h-5 w-5 text-primary" />
              Featured creators
            </h2>
            <p className="text-sm text-muted-foreground mb-3">
              Creators trusted by our community.
            </p>
            <div className="flex flex-wrap gap-2">
              {featuredCreators.map((c) => (
                <Badge key={c.creator_id} variant="secondary" className="py-1.5 px-3">
                  {c.display_name}
                </Badge>
              ))}
            </div>
          </section>
        )}

        <div className="grid gap-6 sm:grid-cols-2 mb-10">
          {trendingTemplates.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary" />
                Trending this week
              </h2>
              <p className="text-sm text-muted-foreground mb-3">
                Templates gaining momentum.
              </p>
              <div className="space-y-2">
                {trendingTemplates.slice(0, 5).map((t) => (
                  <Card
                    key={t.template_id}
                    variant="soft"
                    className="cursor-pointer transition-all hover:shadow-md hover:border-primary/20"
                    onClick={() => setPreviewTemplateId(t.template_id)}
                  >
                    <CardHeader className="py-3">
                      <CardTitle className="font-serif text-sm">{t.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {t.creator_name && <span className="mr-2">{t.creator_name}</span>}
                        {t.activity_count} {t.activity_count === 1 ? 'use' : 'uses'} this week
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </section>
          )}
          {topSellers.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
                <Award className="h-5 w-5 text-primary" />
                Top sellers
              </h2>
              <p className="text-sm text-muted-foreground mb-3">
                Best-selling creator templates.
              </p>
              <div className="space-y-2">
                {topSellers.slice(0, 5).map((t) => (
                  <Card
                    key={t.template_id}
                    variant="soft"
                    className="cursor-pointer transition-all hover:shadow-md hover:border-primary/20"
                    onClick={() => setPreviewTemplateId(t.template_id)}
                  >
                    <CardHeader className="py-3">
                      <CardTitle className="font-serif text-sm">{t.name}</CardTitle>
                      <CardDescription className="text-xs">
                        {t.creator_name && <span className="mr-2">{t.creator_name}</span>}
                        {t.sales} {t.sales === 1 ? 'sale' : 'sales'}
                        {t.revenue_cents > 0 && (
                          <span className="ml-1">· ${(t.revenue_cents / 100).toFixed(0)}</span>
                        )}
                      </CardDescription>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </section>
          )}
        </div>

        {purchasedTemplates.length > 0 && (
          <section className="mb-10">
            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <BookOpen className="h-5 w-5 text-primary" />
              My purchased templates
            </h2>
            <p className="text-sm text-muted-foreground mb-3">
              Templates you own. Accessible anytime.
            </p>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {purchasedTemplates.map((t) => (
                <TemplateLibraryCard
                  key={t.id}
                  template={{ ...t, can_use: true, required_action: null }}
                  onPreview={() => setPreviewTemplateId(t.id)}
                  onApply={() => handleApplyTemplate({ ...t, can_use: true })}
                />
              ))}
            </div>
          </section>
        )}

        <div className="mb-6 space-y-4">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
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
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <select
              value={filterBookType}
              onChange={(e) => setFilterBookType(e.target.value)}
              className="rounded border bg-background px-3 py-1.5 text-sm"
            >
              <option value="">All types</option>
              <option value="fiction">Fiction</option>
              <option value="nonfiction">Nonfiction</option>
              <option value="memoir">Memoir</option>
              <option value="workbook">Workbook</option>
              <option value="business">Business</option>
            </select>
            <Input
              placeholder="Genre"
              value={filterGenre}
              onChange={(e) => setFilterGenre(e.target.value)}
              className="w-32"
            />
            <Input
              type="number"
              placeholder="Min $"
              value={filterPriceMin}
              onChange={(e) => setFilterPriceMin(e.target.value)}
              className="w-20"
            />
            <Input
              type="number"
              placeholder="Max $"
              value={filterPriceMax}
              onChange={(e) => setFilterPriceMax(e.target.value)}
              className="w-20"
            />
            {(filterBookType || filterGenre || filterPriceMin || filterPriceMax) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setFilterBookType('');
                  setFilterGenre('');
                  setFilterPriceMin('');
                  setFilterPriceMax('');
                }}
              >
                Clear filters
              </Button>
            )}
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
        ) : filteredCategories.length === 0 ? (
          <EmptyState
            icon={<LayoutTemplate className="h-6 w-6" />}
            title="No templates available"
            description={
              user?.is_admin
                ? 'The template library is empty. Run `npm run db:seed:templates` to seed templates, or create a project from scratch.'
                : 'The template library is empty. You can still create a new project and start writing from scratch—Authora adapts to your workflow.'
            }
            action={{ label: 'Create project', href: '/dashboard/projects/new' }}
            secondaryAction={
              user?.is_admin ? { label: 'Admin templates', href: '/dashboard/admin/templates' } : undefined
            }
          />
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
                    {previewTemplate.is_paid && previewTemplate.price_cents != null && (
                      <Badge variant="outline" className="text-xs">
                        ${(previewTemplate.price_cents / 100).toFixed(2)}
                      </Badge>
                    )}
                    {previewTemplate.can_use === false && (
                      <Badge variant="outline" className="text-xs border-amber-500/50 text-amber-600 dark:text-amber-400">
                        <Lock className="h-3 w-3 mr-0.5" />
                        Premium
                      </Badge>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-0.5 mt-2 text-xs text-muted-foreground">
                    {previewTemplate.creator_name && (
                      <span className="flex items-center gap-1">
                        <Users className="h-3 w-3" />
                        {previewTemplate.creator_name}
                      </span>
                    )}
                    {(previewTemplate.usage_count ?? 0) > 0 && (
                      <span>{(previewTemplate.usage_count ?? 0)} projects created</span>
                    )}
                    {previewTemplate.rating_avg != null && (previewTemplate.rating_count ?? 0) > 0 && (
                      <span className="flex items-center gap-0.5">
                        <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                        {previewTemplate.rating_avg.toFixed(1)} ({previewTemplate.rating_count} ratings)
                      </span>
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
                      : previewTemplate.required_action?.startsWith('purchase_template:')
                        ? `Purchase this creator template for $${((previewTemplate.price_cents ?? 0) / 100).toFixed(2)}.`
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
                {previewTemplate.can_use ? (
                  <Button onClick={() => handleApplyTemplate(previewTemplate)}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Use this template
                  </Button>
                ) : previewTemplate.required_action?.startsWith('purchase_template:') ? (
                  <Button
                    onClick={() => handlePurchaseTemplate(previewTemplate.id)}
                    disabled={purchasingTemplateId === previewTemplate.id}
                  >
                    {purchasingTemplateId === previewTemplate.id ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <CreditCard className="h-4 w-4 mr-2" />
                    )}
                    Buy for ${((previewTemplate.price_cents ?? 0) / 100).toFixed(2)}
                  </Button>
                ) : (
                  <Button
                    onClick={() => handleApplyTemplate(previewTemplate)}
                    disabled
                  >
                    <Lock className="h-4 w-4 mr-2" />
                    {previewTemplate.required_action === 'upgrade' ? 'Upgrade to unlock' : 'Purchase to unlock'}
                  </Button>
                )}
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
  const usageCount = template.usage_count ?? 0;
  const priceDisplay = template.is_paid && template.price_cents != null
    ? `$${(template.price_cents / 100).toFixed(2)}`
    : null;
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
              <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-1.5 text-xs text-muted-foreground">
                {template.creator_name && (
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" />
                    {template.creator_name}
                  </span>
                )}
                {usageCount > 0 && (
                  <span>{usageCount} {usageCount === 1 ? 'project' : 'projects'} created</span>
                )}
                {priceDisplay && (
                  <span className="font-medium text-foreground">{priceDisplay}</span>
                )}
                {template.rating_avg != null && template.rating_count != null && template.rating_count > 0 && (
                  <span className="flex items-center gap-0.5">
                    <Star className="h-3 w-3 fill-amber-400 text-amber-400" />
                    {template.rating_avg.toFixed(1)} ({template.rating_count})
                  </span>
                )}
              </div>
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
          {priceDisplay && (
            <Badge variant="outline" className="text-xs">
              {priceDisplay}
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
