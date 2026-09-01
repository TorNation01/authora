'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  Sparkles,
  ChevronRight,
  ChevronLeft,
  Zap,
  Compass,
} from 'lucide-react';
import {
  TEMPLATE_LIBRARY,
  START_OPTIONS,
  CUSTOM_PROJECT,
  CATEGORY_DESCRIPTIONS,
  MICROCOPY,
  GUIDANCE_MODES,
} from '@/content/template-copy';
import {
  FRAMEWORK_SELECTION,
  FRAMEWORK_SUPPORTIVE_COPY,
  FRAMEWORK_DESCRIPTIONS,
} from '@/content/framework-copy';
import { TemplatePreviewCard } from '@/components/onboarding/TemplatePreviewCard';
import { StarterTemplateSelector } from '@/components/onboarding/StarterTemplateSelector';
import { MultiSelect } from '@/components/ui/multi-select';
import { GENRE_OPTIONS } from '@/content/genre-options';
import { THEME_OPTIONS } from '@/content/theme-options';
import { useProjectCreateGuard, useLimitErrorHandler, isLimitError } from '@/hooks/use-conversion-triggers';

type TemplateSummary = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  book_type: string | null;
  genre: string | null;
};

type TemplateCategory = {
  category: string;
  name: string;
  slug: string;
  template: TemplateSummary;
  children: TemplateSummary[];
};

const STRUCTURE_OPTIONS: Record<string, string> = {
  three_act: '3-act structure',
  hero_journey: "Hero's journey",
  romance_beats: 'Romance beat structure',
  mystery_thriller: 'Mystery/Thriller structure',
  save_the_cat: 'Save the Cat',
  problem_solution_result: 'Problem → Solution → Result',
  step_by_step: 'Step-by-step transformation',
  authority: 'Authority/credibility book',
  instructional: 'Instructional guide',
  modular: 'Modular teaching framework',
  custom: 'Custom / build your own',
};

type StarterWithTemplateId = {
  id: string;
  slug: string;
  name: string;
  templateSlug: string | null;
  templateId: string | null;
  guidanceLevel: 'guided' | 'flexible' | 'freeform';
  knowledgeMode: 'fiction' | 'nonfiction' | 'memoir' | 'workbook' | 'hybrid';
};

export default function NewProjectPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const templateIdFromUrl = searchParams.get('templateId');
  const { toast } = useToast();
  const projectCreateGuard = useProjectCreateGuard();
  const handleLimitError = useLimitErrorHandler();
  const [mode, setMode] = useState<'starters' | 'quick' | 'wizard'>('starters');
  const [step, setStep] = useState(1);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [featuredLaunch, setFeaturedLaunch] = useState<TemplateSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingCategories, setLoadingCategories] = useState(true);

  // Starter flow: selected starter for quick create or customize
  const [selectedStarter, setSelectedStarter] = useState<StarterWithTemplateId | null>(null);
  const [preselectedTemplateId, setPreselectedTemplateId] = useState<string | null>(templateIdFromUrl);

  // When landing with ?templateId=xxx, switch to wizard and pre-select template
  useEffect(() => {
    if (templateIdFromUrl) {
      setMode('wizard');
      setPreselectedTemplateId(templateIdFromUrl);
    }
  }, [templateIdFromUrl]);

  // Wizard state
  const [selectedCategory, setSelectedCategory] = useState<TemplateCategory | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const [projectName, setProjectName] = useState('');
  const [bookTitle, setBookTitle] = useState('');
  const [coreIdea, setCoreIdea] = useState('');
  const [structureFramework, setStructureFramework] = useState('');
  const [targetWords, setTargetWords] = useState('');
  const [targetDate, setTargetDate] = useState('');
  const [guidanceMode, setGuidanceMode] = useState<'guided' | 'flexible' | 'freeform'>('guided');
  const [genreTags, setGenreTags] = useState<string[]>([]);
  const [themes, setThemes] = useState<string[]>([]);

  useEffect(() => {
    if (mode === 'wizard') {
      Promise.all([
        api<TemplateCategory[]>('/api/v1/templates/categories'),
        api<TemplateSummary[]>('/api/v1/templates/featured-launch'),
        api<{ preferences: Record<string, unknown> }>('/api/v1/auth/me/preferences').catch(() => ({ preferences: {} })),
      ])
        .then(([cats, featured, prefs]) => {
          setCategories(cats);
          setFeaturedLaunch(featured);
          const gm = (prefs?.preferences as Record<string, unknown>)?.onboarding_guidance_mode;
          if (gm === 'guided' || gm === 'flexible' || gm === 'freeform') {
            setGuidanceMode(gm);
          }
          // Apply preselected template from Customize flow
          if (preselectedTemplateId) {
            const fromFeatured = featured.find((t) => t.id === preselectedTemplateId);
            if (fromFeatured) {
              const cat = cats.find(
                (c) => c.template.id === fromFeatured.id || c.children.some((ch) => ch.id === fromFeatured.id)
              );
              if (cat) {
                setSelectedCategory(cat);
                setSelectedTemplateId(fromFeatured.id);
              } else {
                setSelectedCategory({
                  category: fromFeatured.slug,
                  name: fromFeatured.name,
                  slug: fromFeatured.slug,
                  template: fromFeatured,
                  children: [],
                });
                setSelectedTemplateId(fromFeatured.id);
              }
            } else {
              for (const cat of cats) {
                if (cat.template.id === preselectedTemplateId) {
                  setSelectedCategory(cat);
                  setSelectedTemplateId(cat.template.id);
                  break;
                }
                const child = cat.children.find((c) => c.id === preselectedTemplateId);
                if (child) {
                  setSelectedCategory(cat);
                  setSelectedTemplateId(child.id);
                  break;
                }
              }
            }
            setPreselectedTemplateId(null);
          }
        })
        .catch(() => {
          setCategories([]);
          setFeaturedLaunch([]);
        })
        .finally(() => setLoadingCategories(false));
    }
  }, [mode, preselectedTemplateId]);

  async function handleQuickCreate(e: React.FormEvent) {
    e.preventDefault();
    const name = projectName?.trim() || 'Untitled Project';
    const canCreate = await projectCreateGuard();
    if (!canCreate) return;
    setLoading(true);
    try {
      // Blank starter or no template: create minimal project via from-wizard
      if (!selectedStarter?.templateId || selectedStarter.slug === 'blank') {
        const res = await api<{ project: { id: string }; book_id: string }>('/api/v1/projects/from-wizard', {
          method: 'POST',
          body: JSON.stringify({
            template_id: null,
            project_name: name,
            book_title: name,
            book_type: 'fiction',
            guidance_mode: 'freeform',
            knowledge_mode: 'fiction',
          }),
        });
        toast({ title: 'Project created' });
        router.push(`/dashboard/projects/${res.project.id}/books/${res.book_id}/plan`);
        return;
      }
      // Template-based: create from wizard with template
      const res = await api<{ project: { id: string }; book_id: string }>('/api/v1/projects/from-wizard', {
        method: 'POST',
        body: JSON.stringify({
          template_id: selectedStarter.templateId,
          project_name: name,
          book_title: bookTitle?.trim() || name,
          book_type: selectedStarter.knowledgeMode === 'fiction' ? 'fiction' : 'nonfiction',
          genre: null,
          guidance_mode: selectedStarter.guidanceLevel,
          knowledge_mode: selectedStarter.knowledgeMode,
        }),
      });
      toast({ title: 'Project created' });
      router.push(`/dashboard/projects/${res.project.id}/books/${res.book_id}/plan`);
    } catch (err) {
      handleLimitError(err);
      if (!isLimitError(err instanceof Error ? err.message : String(err))) {
        toast({
          title: 'Failed to create project',
          description: err instanceof Error ? err.message : 'Try again',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  }

  const getSelectedTemplate = (): TemplateSummary | null => {
    if (!selectedTemplateId) return null;
    const fromFeatured = featuredLaunch.find((t) => t.id === selectedTemplateId);
    if (fromFeatured) return fromFeatured;
    for (const cat of categories) {
      if (cat.template.id === selectedTemplateId) return cat.template;
      const child = cat.children.find((c) => c.id === selectedTemplateId);
      if (child) return child;
    }
    return null;
  };

  async function handleWizardCreate() {
    if (!projectName.trim()) {
      toast({ title: 'Project name is required', variant: 'destructive' });
      return;
    }
    const canCreate = await projectCreateGuard();
    if (!canCreate) return;
    const template = getSelectedTemplate();
    setLoading(true);
    try {
      const res = await api<{ project: { id: string }; book_id: string; book_title: string }>(
        '/api/v1/projects/from-wizard',
        {
          method: 'POST',
          body: JSON.stringify({
            template_id: guidanceMode === 'freeform' ? null : (selectedTemplateId || null),
            project_name: projectName.trim(),
            book_title: bookTitle.trim() || projectName.trim(),
            book_type: template?.book_type || selectedCategory?.template?.book_type || 'fiction',
            genre: template?.genre || selectedCategory?.template?.genre || null,
            genre_tags: genreTags.length > 0 ? genreTags : null,
            themes: themes.length > 0 ? themes : null,
            core_idea: coreIdea.trim() || null,
            structure_framework: structureFramework || null,
            target_words: targetWords ? parseInt(targetWords, 10) : null,
            target_date: targetDate.trim() || null,
            guidance_mode: guidanceMode,
          }),
        }
      );
      toast({ title: 'Project created' });
      router.push(`/dashboard/projects/${res.project.id}/books/${res.book_id}/plan`);
    } catch (err) {
      handleLimitError(err);
      if (!isLimitError(err instanceof Error ? err.message : String(err))) {
        toast({
          title: 'Failed to create project',
          description: err instanceof Error ? err.message : 'Try again',
          variant: 'destructive',
        });
      }
    } finally {
      setLoading(false);
    }
  }

  const totalSteps = 7;
  const canProceed = () => {
    if (step === 1) return true;
    if (step === 2) return true;
    if (step === 3) return projectName.trim().length > 0;
    if (step === 4) return true;
    if (step === 5) return true;
    if (step === 6) return true;
    if (step === 7) return true;
    return false;
  };

  const nextStep = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    } else {
      handleWizardCreate();
    }
  };

  const prevStep = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const selectCategory = (cat: TemplateCategory, childId?: string) => {
    setSelectedCategory(cat);
    setSelectedTemplateId(childId || cat.template.id);
  };

  const selectFeaturedTemplate = (template: TemplateSummary) => {
    setSelectedTemplateId(template.id);
    const cat = categories.find(
      (c) =>
        c.template.id === template.id ||
        c.children.some((ch) => ch.id === template.id)
    );
    if (cat) setSelectedCategory(cat);
    else {
      setSelectedCategory({
        category: template.slug,
        name: template.name,
        slug: template.slug,
        template,
        children: [],
      });
    }
  };

  // Starter selection (main view)
  if (mode === 'starters') {
    return (
      <div className="w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <PageHeader
          title="Choose your starter"
          description="Start with confidence. Pick a path that matches your book type, or start blank."
          backHref="/dashboard"
          backLabel="Dashboard"
        />
        <p className="mt-2 text-sm text-muted-foreground">{MICROCOPY.adjustLater}</p>
        <div className="mt-8">
          <StarterTemplateSelector
            onUseStarter={(starter) => {
              setSelectedStarter({
                id: starter.id,
                slug: starter.slug,
                name: starter.name,
                templateSlug: starter.templateSlug,
                templateId: starter.templateId,
                guidanceLevel: starter.guidanceLevel,
                knowledgeMode: starter.knowledgeMode,
              });
              setMode('quick');
            }}
            onCustomize={(starter) => {
              if (starter.templateId) {
                setPreselectedTemplateId(starter.templateId);
                setSelectedStarter({
                  id: starter.id,
                  slug: starter.slug,
                  name: starter.name,
                  templateSlug: starter.templateSlug,
                  templateId: starter.templateId,
                  guidanceLevel: starter.guidanceLevel,
                  knowledgeMode: starter.knowledgeMode,
                });
                setMode('wizard');
              }
            }}
            onStartBlank={() => {
              setSelectedStarter({
                id: 'blank',
                slug: 'blank',
                name: 'Blank Project',
                templateSlug: null,
                templateId: null,
                guidanceLevel: 'freeform',
                knowledgeMode: 'fiction',
              });
              setMode('quick');
            }}
          />
        </div>
      </div>
    );
  }

  // Quick create (from starter or blank)
  if (mode === 'quick') {
    const isBlank = !selectedStarter?.templateId || selectedStarter.slug === 'blank';
    return (
      <div className="p-6 lg:p-8 max-w-xl">
        <PageHeader
          title={isBlank ? 'Start blank' : `Use ${selectedStarter?.name ?? 'starter'}`}
          description={
            isBlank
              ? 'Name your project and create a minimal workspace.'
              : 'Name your project and create with the preconfigured structure.'
          }
          backHref="/dashboard/projects/new"
          backLabel="Back"
        />
        <p className="mt-2 text-sm text-muted-foreground">{MICROCOPY.startSimple}</p>
        <Card variant="sanctuary" className="mt-6">
          <CardHeader>
            <CardTitle className="font-serif">Project name</CardTitle>
            <CardDescription>
              e.g. &quot;My first novel&quot; or &quot;Business book 2025&quot;
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleQuickCreate} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="name">Name</Label>
                <Input
                  id="name"
                  placeholder="My Novel"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  required
                  className="h-11"
                />
              </div>
              {!isBlank && (
                <div className="space-y-2">
                  <Label htmlFor="bookTitle">Book title (optional)</Label>
                  <Input
                    id="bookTitle"
                    placeholder="Same as project name"
                    value={bookTitle}
                    onChange={(e) => setBookTitle(e.target.value)}
                    className="h-11"
                  />
                </div>
              )}
              <div className="flex gap-3">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create project'}
                </Button>
                <Button variant="outline" type="button" onClick={() => setMode('starters')}>
                  Back
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Wizard (Guided setup)
  return (
    <div className="p-6 lg:p-8 max-w-2xl">
      <PageHeader
        title={selectedStarter ? `Customize: ${selectedStarter.name}` : START_OPTIONS.guidedSetup.label}
        description={`Step ${step} of ${totalSteps}`}
        backHref={step === 1 ? '/dashboard/projects/new' : undefined}
        backLabel={step === 1 ? 'Back' : undefined}
      />

      <div className="mt-6 mb-4">
        <div className="flex gap-1">
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div
              key={i}
              className={`h-1 flex-1 rounded-full transition-colors ${
                i + 1 <= step ? 'bg-primary' : 'bg-muted'
              }`}
            />
          ))}
        </div>
      </div>

      <Card variant="sanctuary" className="mt-4">
        <CardHeader>
          <CardTitle className="font-serif">
            {step === 1 && 'Choose project type'}
            {step === 2 && (selectedCategory?.children.length ? 'Choose genre or sub-type' : 'Name your project')}
            {step === 3 && 'Name your project'}
            {step === 4 && 'Define your core idea'}
            {step === 5 && FRAMEWORK_SELECTION.heading}
            {step === 6 && 'Set your writing goals'}
            {step === 7 && 'Ready to create'}
          </CardTitle>
          <CardDescription>
            {step === 1 && 'What kind of book are you writing?'}
            {step === 2 && 'Shape your story with genres and themes.'}
            {step === 3 && 'Give your project a name.'}
            {step === 4 && 'One sentence about what this book is about.'}
            {step === 5 && FRAMEWORK_SELECTION.subheading}
            {step === 6 && 'Optional: set a word goal and target date.'}
            {step === 7 && 'Review and create your project.'}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {step === 1 && (
            <div className="space-y-6">
              <div className="space-y-3">
                <p className="text-sm font-medium">{GUIDANCE_MODES.heading}</p>
                <p className="text-xs text-muted-foreground">{GUIDANCE_MODES.chooseAmount}</p>
                <p className="text-xs text-muted-foreground">{GUIDANCE_MODES.changeLater}</p>
                <div className="flex flex-wrap gap-2">
                  {(['guided', 'flexible', 'freeform'] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setGuidanceMode(m)}
                      className={`rounded-lg border-2 px-4 py-3 text-left text-sm transition-colors ${
                        guidanceMode === m
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border hover:border-primary/50 hover:bg-muted/50'
                      }`}
                    >
                      <span className="font-medium block">{GUIDANCE_MODES[m].label}</span>
                      <span className="text-xs text-muted-foreground line-clamp-2">
                        {GUIDANCE_MODES[m].description}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
              <TemplatePreviewCard
                templateId={selectedTemplateId}
                templateName={getSelectedTemplate()?.name}
              />
              <p className="text-sm text-muted-foreground">{MICROCOPY.keepMoving}</p>
              {featuredLaunch.length > 0 && (
                <div>
                  <p className="mb-3 text-sm font-medium text-muted-foreground">
                    Recommended for launch
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {featuredLaunch.map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => selectFeaturedTemplate(t)}
                        className={`rounded-full border-2 px-4 py-2 text-sm font-medium transition-colors ${
                          selectedTemplateId === t.id
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border hover:border-primary/50 hover:bg-muted/50'
                        }`}
                      >
                        {t.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <p className="mb-3 text-sm font-medium text-muted-foreground">
                  All project types
                </p>
                <div className="grid gap-3 sm:grid-cols-2">
              {loadingCategories ? (
                <p className="text-muted-foreground col-span-2">Loading templates...</p>
              ) : (
                categories.map((cat) => (
                  <div key={cat.slug} className="space-y-2">
                    <button
                      type="button"
                      onClick={() => selectCategory(cat)}
                      className={`w-full text-left rounded-lg border-2 p-4 transition-colors ${
                        selectedCategory?.slug === cat.slug && !selectedTemplateId?.startsWith(cat.slug + '-')
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-muted-foreground/30'
                      }`}
                    >
                      <span className="font-medium block">{cat.name}</span>
                      {cat.template.description && (
                        <span className="text-sm text-muted-foreground line-clamp-2">
                          {cat.template.description}
                        </span>
                      )}
                    </button>
                    {cat.children.length > 0 && selectedCategory?.slug === cat.slug && (
                      <div className="pl-2 space-y-1">
                        {cat.children.map((child) => (
                          <button
                            key={child.id}
                            type="button"
                            onClick={() => selectCategory(cat, child.id)}
                            className={`block w-full text-left rounded px-3 py-2 text-sm ${
                              selectedTemplateId === child.id
                                ? 'bg-primary/10 text-primary font-medium'
                                : 'hover:bg-muted'
                            }`}
                          >
                            {child.name}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}
                </div>
              </div>
            </div>
          )}

          {step === 2 && selectedCategory && (
            <div className="space-y-5">
              {/* Instructional banner */}
              <div className="rounded-lg border bg-gradient-to-r from-purple-50/50 to-blue-50/50 dark:from-purple-950/20 dark:to-blue-950/20 p-4">
                <h3 className="text-sm font-semibold mb-1.5">🎨 Shape your story's DNA</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Pick your <strong>primary genre</strong> below — this sets your starting template and framework.
                  Then <strong>blend in additional genres</strong> and <strong>themes</strong> to create something
                  uniquely yours. A thriller/romance/fantasy with dystopian themes? Go for it.
                </p>
                <p className="text-xs text-muted-foreground mt-1.5">
                  You can change any of this later from your project dashboard.
                </p>
              </div>

              {selectedCategory.children.length > 0 && (
                <div className="space-y-2">
                  <Label>Primary genre</Label>
                  <Select value={selectedTemplateId || ''} onValueChange={setSelectedTemplateId}>
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select genre" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={selectedCategory.template.id}>
                        {selectedCategory.template.name} (general)
                      </SelectItem>
                      {selectedCategory.children.map((c) => (
                        <SelectItem key={c.id} value={c.id}>
                          {c.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <MultiSelect
                value={genreTags}
                onChange={setGenreTags}
                options={GENRE_OPTIONS}
                label="Genre blend"
                placeholder="Add genres to blend..."
              />
              <MultiSelect
                value={themes}
                onChange={setThemes}
                options={THEME_OPTIONS}
                label="Themes"
                placeholder="Add themes..."
              />
            </div>
          )}

          {step === 3 && selectedCategory && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="projectName">Project name</Label>
                <Input
                  id="projectName"
                  placeholder="My Novel"
                  value={projectName}
                  onChange={(e) => setProjectName(e.target.value)}
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="bookTitle">Book title (optional)</Label>
                <Input
                  id="bookTitle"
                  placeholder="Same as project or different"
                  value={bookTitle}
                  onChange={(e) => setBookTitle(e.target.value)}
                  className="h-11"
                />
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-2">
              <Label htmlFor="coreIdea">Core idea or goal</Label>
              <p className="text-xs text-muted-foreground">{MICROCOPY.adjustLater}</p>
              <Textarea
                id="coreIdea"
                placeholder="One sentence: what is this book about? What transformation or story do you want to tell?"
                value={coreIdea}
                onChange={(e) => setCoreIdea(e.target.value)}
                rows={4}
                className="resize-none"
              />
            </div>
          )}

          {step === 5 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{FRAMEWORK_SUPPORTIVE_COPY[0]}</p>
              <div className="space-y-2">
                <Label>Structure framework (optional)</Label>
                <Select value={structureFramework} onValueChange={setStructureFramework}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Choose or skip" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(STRUCTURE_OPTIONS)
                      .filter(([k]) => k === 'custom' || (!k.startsWith('custom') && k !== 'custom_fiction' && k !== 'custom_nonfiction'))
                      .map(([value, label]) => (
                        <SelectItem key={value} value={value}>
                          {label}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                {structureFramework && FRAMEWORK_DESCRIPTIONS[structureFramework] && (
                  <p className="text-sm text-muted-foreground">
                    {FRAMEWORK_DESCRIPTIONS[structureFramework]}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">{FRAMEWORK_SUPPORTIVE_COPY[4]}</p>
              </div>
            </div>
          )}

          {step === 6 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{MICROCOPY.momentum}</p>
              <div className="space-y-2">
                <Label htmlFor="targetWords">Target word count (optional)</Label>
                <Input
                  id="targetWords"
                  type="number"
                  placeholder="e.g. 80000"
                  value={targetWords}
                  onChange={(e) => setTargetWords(e.target.value)}
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetDate">Target completion date (optional)</Label>
                <Input
                  id="targetDate"
                  type="date"
                  value={targetDate}
                  onChange={(e) => setTargetDate(e.target.value)}
                  className="h-11"
                />
              </div>
            </div>
          )}

          {step === 7 && (
            <div className="space-y-4 rounded-lg border bg-muted/30 p-4">
              <p className="font-medium">Summary</p>
              <dl className="space-y-2 text-sm">
                <div>
                  <dt className="text-muted-foreground">Project</dt>
                  <dd>{projectName || '—'}</dd>
                </div>
                <div>
                  <dt className="text-muted-foreground">Template</dt>
                  <dd>
                    {selectedCategory
                      ? (selectedCategory.children.find((ch) => ch.id === selectedTemplateId)?.name ||
                        (selectedCategory.slug === 'custom-blank' ? CUSTOM_PROJECT.label : selectedCategory.template.name))
                      : CUSTOM_PROJECT.label}
                  </dd>
                </div>
                {coreIdea && (
                  <div>
                    <dt className="text-muted-foreground">Core idea</dt>
                    <dd className="line-clamp-2">{coreIdea}</dd>
                  </div>
                )}
                {targetWords && (
                  <div>
                    <dt className="text-muted-foreground">Target words</dt>
                    <dd>{targetWords}</dd>
                  </div>
                )}
              </dl>
            </div>
          )}

          <div className="flex gap-3 pt-4">
            {step > 1 ? (
              <Button variant="outline" onClick={prevStep} type="button">
                <ChevronLeft className="mr-1 h-4 w-4" />
                Back
              </Button>
            ) : null}
            <Button
              onClick={nextStep}
              disabled={step === 3 && !projectName.trim()}
              type="button"
              className="ml-auto"
            >
              {step === totalSteps ? (
                loading ? (
                  'Creating...'
                ) : (
                  <>
                    Create project
                    <Sparkles className="ml-1 h-4 w-4" />
                  </>
                )
              ) : (
                <>
                  Next
                  <ChevronRight className="ml-1 h-4 w-4" />
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
