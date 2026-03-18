'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { api } from '@/lib/api';
import {
  Compass,
  Zap,
  BookOpen,
  Target,
  PenLine,
  LayoutList,
  FileText,
  Check,
  Loader2,
  ChevronRight,
  ChevronLeft,
  Sparkles,
} from 'lucide-react';
import {
  ONBOARDING_ENTRY,
  ONBOARDING_INTENT,
  ONBOARDING_GUIDANCE,
  ONBOARDING_PROJECT,
  ONBOARDING_STRUCTURE,
  ONBOARDING_FIRST_ACTION,
  ONBOARDING_SKIP,
} from '@/content/onboarding-copy';
import { EditorIntroOverlay, hasSeenEditorIntro } from '@/components/onboarding/EditorIntroOverlay';

type IntentType = 'fiction' | 'nonfiction' | 'memoir' | 'workbook' | 'not_sure';
type GuidanceType = 'guided' | 'balanced' | 'freeform';
type StructureChoice = 'template' | 'blank';
type FirstAction = 'write' | 'outline';

interface OnboardingData {
  entry: 'guided' | 'quick';
  intent: IntentType;
  guidance: GuidanceType;
  projectName: string;
  projectDescription: string;
  projectGoal: string;
  structure: StructureChoice;
  templateId: string | null;
  firstAction: FirstAction;
}

type TemplateSummary = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  book_type: string | null;
  category?: string;
};

const ONBOARDING_PREF_KEY = 'authora_onboarding_progress_v2';

function loadProgress(): { stepIndex: number; data: Partial<OnboardingData> } | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(ONBOARDING_PREF_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as { stepIndex: number; data: Partial<OnboardingData> };
  } catch {
    return null;
  }
}

function saveProgress(stepIndex: number, data: Partial<OnboardingData>) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(ONBOARDING_PREF_KEY, JSON.stringify({ stepIndex, data }));
  } catch {
    /* ignore */
  }
}

function clearProgress() {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(ONBOARDING_PREF_KEY);
  } catch {
    /* ignore */
  }
}

const INTENT_TO_BOOK_TYPE: Record<IntentType, string> = {
  fiction: 'fiction',
  nonfiction: 'nonfiction',
  memoir: 'nonfiction',
  workbook: 'nonfiction',
  not_sure: 'fiction',
};

const INTENT_TO_KNOWLEDGE: Record<IntentType, string> = {
  fiction: 'fiction',
  nonfiction: 'nonfiction',
  memoir: 'memoir',
  workbook: 'workbook',
  not_sure: 'fiction',
};

const GUIDANCE_TO_API: Record<GuidanceType, string> = {
  guided: 'guided',
  balanced: 'flexible',
  freeform: 'freeform',
};

const GUIDED_STEPS = [
  { id: 'entry', title: 'How to start', icon: Compass },
  { id: 'intent', title: 'What are you writing?', icon: BookOpen },
  { id: 'guidance', title: 'Guidance level', icon: Target },
  { id: 'project', title: 'Project setup', icon: PenLine },
  { id: 'structure', title: 'Structure', icon: LayoutList },
  { id: 'first_action', title: 'First action', icon: FileText },
];

export default function OnboardingPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [data, setData] = useState<Partial<OnboardingData>>({
    entry: 'guided',
    intent: 'fiction',
    guidance: 'guided',
    projectName: '',
    projectDescription: '',
    projectGoal: '',
    structure: 'blank',
    templateId: null,
    firstAction: 'write',
  });
  const [submitting, setSubmitting] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [allTemplates, setAllTemplates] = useState<TemplateSummary[]>([]);
  const [showIntroOverlay, setShowIntroOverlay] = useState(false);
  const [redirectUrl, setRedirectUrl] = useState<string | null>(null);
  const router = useRouter();

  const isQuickStart = data.entry === 'quick';
  const steps = isQuickStart ? [{ id: 'entry', title: 'Quick Start', icon: Zap }] : GUIDED_STEPS;
  const currentStep = steps[stepIndex];
  const totalSteps = steps.length;
  const progress = ((stepIndex + 1) / totalSteps) * 100;

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!localStorage.getItem('access_token')) {
      router.replace('/login');
    }
  }, [router]);

  useEffect(() => {
    const saved = loadProgress();
    if (saved && saved.stepIndex > 0 && saved.data) {
      setStepIndex(Math.min(saved.stepIndex, steps.length - 1));
      setData((d) => ({ ...d, ...saved.data }));
    }
  }, []);

  useEffect(() => {
    api<{ step_index: number; data: Record<string, unknown> }>('/api/v1/journey/onboarding/progress')
      .then((res) => {
        if (res.step_index > 0 && res.data && Object.keys(res.data).length > 0) {
          const merged = { ...data, ...res.data } as Partial<OnboardingData>;
          setData(merged);
          const idx = Math.min(res.step_index, steps.length - 1);
          setStepIndex(idx);
          saveProgress(idx, merged);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (stepIndex > 0 && stepIndex < steps.length - 1) {
      saveProgress(stepIndex, data);
    }
  }, [stepIndex, data]);

  const intentStepIndex = steps.findIndex((s) => s.id === 'intent');

  useEffect(() => {
    const atOrPastIntent = intentStepIndex >= 0 && stepIndex >= intentStepIndex;
    const shouldFetch = data.intent && (atOrPastIntent || data.structure === 'template');
    if (!shouldFetch) return;
    setLoadingTemplates(true);
    const load = async () => {
      try {
        const flat = await api<unknown>('/api/v1/templates/all');
        const arr = Array.isArray(flat) ? flat : [];
        setAllTemplates(arr as TemplateSummary[]);
      } catch {
        setAllTemplates([]);
      } finally {
        setLoadingTemplates(false);
      }
    };
    load();
  }, [data.structure, data.intent, stepIndex, intentStepIndex]);

  const selectableTemplates: { id: string; name: string; description: string | null }[] = (() => {
    const intent = data.intent || 'fiction';
    const slug = (s: string) => (s || '').toLowerCase();
    const cat = (t: TemplateSummary) => (t.category || '').toLowerCase();

    const filtered = allTemplates.filter((t) => {
      if (intent === 'not_sure') return true;
      if (intent === 'fiction') return slug(t.slug).includes('fiction') || cat(t) === 'fiction';
      if (intent === 'nonfiction')
        return (
          slug(t.slug).includes('nonfiction') ||
          slug(t.slug).includes('business') ||
          slug(t.slug).includes('self-help') ||
          cat(t) === 'nonfiction' ||
          cat(t) === 'business'
        );
      if (intent === 'memoir') return slug(t.slug).includes('memoir') || cat(t) === 'memoir';
      if (intent === 'workbook') return slug(t.slug).includes('workbook') || cat(t) === 'workbook';
      return true;
    });

    const list = filtered.length > 0 ? filtered : allTemplates;
    return list.map((t) => ({
      id: typeof t.id === 'string' ? t.id : String(t.id),
      name: t.name,
      description: t.description,
    }));
  })();

  const canProceed = useCallback(() => {
    switch (currentStep?.id) {
      case 'entry':
        return true;
      case 'intent':
        return !!data.intent;
      case 'guidance':
        return !!data.guidance;
      case 'project':
        return !!(data.projectName?.trim());
      case 'structure':
        if (data.structure === 'template') {
          return !!data.templateId || selectableTemplates.length === 0;
        }
        return true;
      case 'first_action':
        return !!data.firstAction;
      default:
        return true;
    }
  }, [currentStep?.id, data, selectableTemplates.length]);

  const createProject = useCallback(
    async (firstAction: FirstAction) => {
      const name = data.projectName?.trim() || 'My Book';
      const bookType = INTENT_TO_BOOK_TYPE[data.intent || 'fiction'];
      const knowledgeMode = INTENT_TO_KNOWLEDGE[data.intent || 'fiction'];
      const guidanceMode = GUIDANCE_TO_API[data.guidance || 'guided'];

      const res = await api<{ project: { id: string }; book_id: string }>('/api/v1/projects/from-wizard', {
        method: 'POST',
        body: JSON.stringify({
          template_id: data.templateId || null,
          project_name: name,
          book_title: name,
          book_type: bookType,
          knowledge_mode: knowledgeMode,
          core_idea: data.projectDescription?.trim() || null,
          guidance_mode: guidanceMode,
        }),
      });

      const url =
        firstAction === 'write'
          ? `/dashboard/projects/${res.project.id}/books/${res.book_id}`
          : `/dashboard/projects/${res.project.id}/books/${res.book_id}/plan`;
      return url;
    },
    [data]
  );

  const handleComplete = async () => {
    setSubmitting(true);
    try {
      await api('/api/v1/journey/onboarding', {
        method: 'POST',
        body: JSON.stringify({
          book_type: INTENT_TO_BOOK_TYPE[data.intent || 'fiction'],
          guidance_mode: GUIDANCE_TO_API[data.guidance || 'guided'],
          writing_mode: 'solo',
        }),
      });
      await api('/api/v1/auth/me/preferences', {
        method: 'PATCH',
        body: JSON.stringify({
          preferences: {
            onboarding_completed: true,
            onboarding_guidance_mode: GUIDANCE_TO_API[data.guidance || 'guided'],
            onboarding_progress: null,
          },
        }),
      });
      clearProgress();

      const firstAction = data.firstAction || 'write';
      const url = await createProject(firstAction);

      if (firstAction === 'write' && !hasSeenEditorIntro()) {
        setRedirectUrl(url);
        setShowIntroOverlay(true);
      } else {
        router.push(url);
      }
    } catch (e) {
      console.error(e);
      setSubmitting(false);
    }
  };

  const handleQuickStartComplete = async () => {
    setSubmitting(true);
    try {
      const name = data.projectName?.trim() || 'Untitled Project';
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
      await api('/api/v1/auth/me/preferences', {
        method: 'PATCH',
        body: JSON.stringify({
          preferences: { onboarding_completed: true, onboarding_progress: null },
        }),
      });
      clearProgress();

      const url = `/dashboard/projects/${res.project.id}/books/${res.book_id}`;
      if (!hasSeenEditorIntro()) {
        setRedirectUrl(url);
        setShowIntroOverlay(true);
      } else {
        router.push(url);
      }
    } catch (e) {
      console.error(e);
      setSubmitting(false);
    }
  };

  const handleIntroComplete = () => {
    setShowIntroOverlay(false);
    if (redirectUrl) router.push(redirectUrl);
  };

  const handleNext = () => {
    if (isQuickStart && currentStep?.id === 'entry') {
      setStepIndex(0);
      setData((d) => ({ ...d, entry: 'quick' }));
      return;
    }

    if (currentStep?.id === 'first_action' || (isQuickStart && currentStep?.id === 'entry')) {
      if (isQuickStart) {
        setData((d) => ({ ...d, projectName: d.projectName || 'Untitled Project' }));
        handleQuickStartComplete();
      } else {
        handleComplete();
      }
      return;
    }

    const nextIdx = stepIndex + 1;
    saveProgress(nextIdx, data);
    api('/api/v1/journey/onboarding/progress', {
      method: 'POST',
      body: JSON.stringify({ step_index: nextIdx, data }),
    }).catch(() => {});
    setStepIndex(nextIdx);
  };

  const handleBack = () => {
    if (stepIndex > 0) setStepIndex(stepIndex - 1);
  };

  const handleEntrySelect = (entry: 'guided' | 'quick') => {
    setData((d) => ({ ...d, entry }));
    if (entry === 'quick') {
      setStepIndex(0);
    }
  };

  const Icon = currentStep?.icon ?? Compass;

  if (showIntroOverlay) {
    return (
      <EditorIntroOverlay
        onComplete={handleIntroComplete}
        onSkip={handleIntroComplete}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-muted/20 to-background p-4">
      <div className="w-full max-w-xl">
        <Link
          href="/dashboard"
          className="mb-8 inline-block font-serif text-xl font-bold text-foreground hover:text-primary transition-colors"
        >
          AUTHORA
        </Link>
        <Card variant="sanctuary" className="shadow-lg">
          <CardHeader>
            {!isQuickStart && (
              <Progress value={progress} showLabel size="sm" className="mb-4" />
            )}
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-2">
              <Icon className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-serif">{currentStep?.title}</CardTitle>
            <CardDescription className="text-base">
              {currentStep?.id === 'entry' && ONBOARDING_ENTRY.subheading}
              {currentStep?.id === 'intent' && ONBOARDING_INTENT.subheading}
              {currentStep?.id === 'guidance' && ONBOARDING_GUIDANCE.subheading}
              {currentStep?.id === 'project' && ONBOARDING_PROJECT.subheading}
              {currentStep?.id === 'structure' && ONBOARDING_STRUCTURE.subheading}
              {currentStep?.id === 'first_action' && ONBOARDING_FIRST_ACTION.subheading}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Entry */}
            {currentStep?.id === 'entry' && (
              <div className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => handleEntrySelect('guided')}
                    className={`rounded-xl border-2 p-5 text-left transition-colors ${
                      data.entry === 'guided'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Compass className="h-5 w-5 text-primary" />
                      <span className="font-semibold">{ONBOARDING_ENTRY.guided.label}</span>
                      {ONBOARDING_ENTRY.guided.recommended && (
                        <span className="rounded-full bg-primary/20 px-2 py-0.5 text-xs font-medium text-primary">
                          Recommended
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{ONBOARDING_ENTRY.guided.desc}</p>
                    <p className="text-xs text-muted-foreground mt-2">{ONBOARDING_ENTRY.guided.benefit}</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => handleEntrySelect('quick')}
                    className={`rounded-xl border-2 p-5 text-left transition-colors ${
                      data.entry === 'quick'
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <Zap className="h-5 w-5 text-primary" />
                      <span className="font-semibold">{ONBOARDING_ENTRY.quick.label}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">{ONBOARDING_ENTRY.quick.desc}</p>
                    <p className="text-xs text-muted-foreground mt-2">{ONBOARDING_ENTRY.quick.benefit}</p>
                  </button>
                </div>
                {data.entry === 'quick' && (
                  <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
                    <Label className="text-sm font-medium">Project name</Label>
                    <Input
                      placeholder={ONBOARDING_PROJECT.namePlaceholder}
                      value={data.projectName || ''}
                      onChange={(e) => setData((d) => ({ ...d, projectName: e.target.value }))}
                      className="mt-2 h-11"
                    />
                  </div>
                )}
              </div>
            )}

            {/* Intent */}
            {currentStep?.id === 'intent' && (
              <div className="grid gap-3 sm:grid-cols-2">
                {(['fiction', 'nonfiction', 'memoir', 'workbook', 'not_sure'] as const).map((key) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, intent: key }))}
                    className={`rounded-xl border-2 p-4 text-left transition-colors ${
                      data.intent === key ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium">{ONBOARDING_INTENT[key].label}</span>
                    <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_INTENT[key].desc}</p>
                  </button>
                ))}
              </div>
            )}

            {/* Guidance */}
            {currentStep?.id === 'guidance' && (
              <div className="space-y-3">
                {(['guided', 'balanced', 'freeform'] as const).map((key) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, guidance: key }))}
                    className={`w-full rounded-xl border-2 p-4 text-left transition-colors ${
                      data.guidance === key ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium">{ONBOARDING_GUIDANCE[key].label}</span>
                    <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_GUIDANCE[key].desc}</p>
                  </button>
                ))}
              </div>
            )}

            {/* Project setup */}
            {currentStep?.id === 'project' && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="projectName">Project name *</Label>
                  <Input
                    id="projectName"
                    placeholder={ONBOARDING_PROJECT.namePlaceholder}
                    value={data.projectName || ''}
                    onChange={(e) => setData((d) => ({ ...d, projectName: e.target.value }))}
                    className="h-11"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="projectDesc">Description (optional)</Label>
                  <Textarea
                    id="projectDesc"
                    placeholder={ONBOARDING_PROJECT.descriptionPlaceholder}
                    value={data.projectDescription || ''}
                    onChange={(e) => setData((d) => ({ ...d, projectDescription: e.target.value }))}
                    rows={2}
                    className="resize-none"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="projectGoal">Goal (optional)</Label>
                  <Input
                    id="projectGoal"
                    placeholder={ONBOARDING_PROJECT.goalPlaceholder}
                    value={data.projectGoal || ''}
                    onChange={(e) => setData((d) => ({ ...d, projectGoal: e.target.value }))}
                    className="h-11"
                  />
                </div>
              </div>
            )}

            {/* Structure */}
            {currentStep?.id === 'structure' && (
              <div className="space-y-4">
                <div className="grid gap-3 sm:grid-cols-2">
                  <button
                    type="button"
                    onClick={() => setData((d) => ({ ...d, structure: 'template', templateId: null }))}
                    className={`rounded-xl border-2 p-4 text-left transition-colors ${
                      data.structure === 'template' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium">{ONBOARDING_STRUCTURE.useTemplate.label}</span>
                    <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_STRUCTURE.useTemplate.desc}</p>
                  </button>
                  <button
                    type="button"
                    onClick={() => setData((d) => ({ ...d, structure: 'blank', templateId: null }))}
                    className={`rounded-xl border-2 p-4 text-left transition-colors ${
                      data.structure === 'blank' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium">{ONBOARDING_STRUCTURE.startBlank.label}</span>
                    <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_STRUCTURE.startBlank.desc}</p>
                  </button>
                </div>
                {data.structure === 'template' && (
                  <div className="space-y-2">
                    <Label>Choose a template</Label>
                    {loadingTemplates ? (
                      <p className="text-sm text-muted-foreground">Loading templates...</p>
                    ) : (
                      <div className="grid gap-2 max-h-48 overflow-y-auto">
                        {selectableTemplates.map((tpl) => (
                          <button
                            key={tpl.id}
                            type="button"
                            onClick={() => setData((d) => ({ ...d, templateId: tpl.id }))}
                            className={`rounded-lg border p-3 text-left transition-colors ${
                              data.templateId === tpl.id ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                            }`}
                          >
                            <span className="font-medium text-sm">{tpl.name}</span>
                            {tpl.description && (
                              <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{tpl.description}</p>
                            )}
                          </button>
                        ))}
                        {selectableTemplates.length === 0 && !loadingTemplates && (
                          <p className="text-sm text-muted-foreground">No templates found. Start blank instead.</p>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* First action */}
            {currentStep?.id === 'first_action' && (
              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() => setData((d) => ({ ...d, firstAction: 'write' }))}
                  className={`rounded-xl border-2 p-5 text-left transition-colors ${
                    data.firstAction === 'write' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                  }`}
                >
                  <PenLine className="h-6 w-6 text-primary mb-2" />
                  <span className="font-medium">{ONBOARDING_FIRST_ACTION.write.label}</span>
                  <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_FIRST_ACTION.write.desc}</p>
                </button>
                <button
                  type="button"
                  onClick={() => setData((d) => ({ ...d, firstAction: 'outline' }))}
                  className={`rounded-xl border-2 p-5 text-left transition-colors ${
                    data.firstAction === 'outline' ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                  }`}
                >
                  <LayoutList className="h-6 w-6 text-primary mb-2" />
                  <span className="font-medium">{ONBOARDING_FIRST_ACTION.outline.label}</span>
                  <p className="text-sm text-muted-foreground mt-1">{ONBOARDING_FIRST_ACTION.outline.desc}</p>
                </button>
              </div>
            )}

            <div className="flex gap-3 pt-4">
              <Button
                className="flex-1"
                onClick={handleNext}
                disabled={!canProceed() || submitting}
              >
                {submitting ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : currentStep?.id === 'first_action' || (isQuickStart && data.entry === 'quick') ? (
                  <Sparkles className="h-4 w-4 mr-2" />
                ) : (
                  <ChevronRight className="h-4 w-4 mr-2" />
                )}
                {submitting
                  ? 'Creating...'
                  : currentStep?.id === 'first_action' || (isQuickStart && data.entry === 'quick')
                    ? 'Start writing'
                    : 'Continue'}
              </Button>
              {stepIndex > 0 && !isQuickStart && (
                <Button variant="ghost" onClick={handleBack} disabled={submitting}>
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
              )}
              {currentStep?.id !== 'entry' && (
                <Button variant="link" asChild>
                  <Link href="/dashboard">{ONBOARDING_SKIP.skip}</Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
        <p className="mt-4 text-center">
          <Link
            href="/onboarding/restart"
            className="text-xs text-muted-foreground hover:text-foreground"
          >
            Restart onboarding
          </Link>
        </p>
      </div>
    </div>
  );
}
