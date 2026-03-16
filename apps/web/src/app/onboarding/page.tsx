'use client';

import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { api } from '@/lib/api';
import {
  BookOpen,
  PenLine,
  Bot,
  User,
  Target,
  Calendar,
  Clock,
  Heart,
  Sparkles,
  Check,
  Loader2,
  ChevronRight,
  ChevronLeft,
} from 'lucide-react';
import {
  ONBOARDING_WELCOME,
  WRITER_TYPES,
  PROJECT_TYPE_STEP,
  GUIDANCE_STEP,
  WORK_STYLE_STEP,
  PACE_STEP,
  COMPLETE_STEP,
  ONBOARDING_SKIP,
} from '@/content/onboarding-copy';

interface OnboardingData {
  writer_type: string;
  book_type: string;
  writing_mode: string;
  writing_goals: string;
  target_timeline: string;
  writing_schedule: string;
  accountability_style: string;
  ai_comfort_level: string;
  genre_topic: string;
  guidance_mode: string;
}

const STEPS = [
  { id: 'welcome', title: 'Welcome', icon: BookOpen },
  { id: 'writer_type', title: 'What kind of writer?', icon: User },
  { id: 'book_type', title: 'What are you writing?', icon: BookOpen },
  { id: 'guidance', title: 'How much guidance?', icon: Target },
  { id: 'work_style', title: 'How do you like to work?', icon: PenLine },
  { id: 'pace', title: 'Set your pace', icon: Calendar },
  { id: 'complete', title: "You're all set", icon: Check },
];

const WRITER_TYPE_OPTIONS = [
  { ...WRITER_TYPES.firstTime, id: 'first_time' as const },
  { ...WRITER_TYPES.experienced, id: 'experienced' as const },
  { ...WRITER_TYPES.fiction, id: 'fiction' as const },
  { ...WRITER_TYPES.nonfiction, id: 'nonfiction' as const },
  { ...WRITER_TYPES.memoir, id: 'memoir' as const },
  { ...WRITER_TYPES.workbook, id: 'workbook' as const },
  { ...WRITER_TYPES.ghostwriter, id: 'ghostwriter' as const },
  { ...WRITER_TYPES.collaborative, id: 'collaborative' as const },
  { ...WRITER_TYPES.notSure, id: 'not_sure' as const },
];

const TIMELINE_OPTIONS = [
  { id: '1 month', label: '1 month' },
  { id: '3 months', label: '3 months' },
  { id: '6 months', label: '6 months' },
  { id: '1 year', label: '1 year' },
  { id: 'no deadline', label: 'No deadline' },
];

const SCHEDULE_OPTIONS = [
  { id: 'mornings', label: 'Mornings' },
  { id: 'evenings', label: 'Evenings' },
  { id: 'weekends', label: 'Weekends' },
  { id: 'daily', label: 'Daily' },
  { id: 'flexible', label: 'Flexible' },
];

const ACCOUNTABILITY_OPTIONS = [
  { id: 'none', label: PACE_STEP.none, desc: PACE_STEP.noneDesc },
  { id: 'gentle', label: PACE_STEP.gentle, desc: PACE_STEP.gentleDesc },
  { id: 'structured', label: PACE_STEP.structured, desc: PACE_STEP.structuredDesc },
  { id: 'buddy', label: PACE_STEP.buddy, desc: PACE_STEP.buddyDesc },
];

const ONBOARDING_PREF_KEY = 'authora_onboarding_progress';

function loadProgress(): { stepIndex: number; data: OnboardingData } | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(ONBOARDING_PREF_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as { stepIndex: number; data: OnboardingData };
  } catch {
    return null;
  }
}

function saveProgress(stepIndex: number, data: OnboardingData) {
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

export default function OnboardingPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    writer_type: '',
    book_type: '',
    writing_mode: '',
    writing_goals: '',
    target_timeline: '',
    writing_schedule: '',
    accountability_style: '',
    ai_comfort_level: 'moderate',
    genre_topic: '',
    guidance_mode: 'guided',
  });
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!localStorage.getItem('access_token')) {
      router.replace('/login');
    }
  }, [router]);

  useEffect(() => {
    const saved = loadProgress();
    if (saved && saved.stepIndex > 0) {
      setStepIndex(saved.stepIndex);
      setData(saved.data);
      return;
    }
    api<{ step_index: number; data: Record<string, unknown> }>('/api/v1/journey/onboarding/progress')
      .then((res) => {
        if (res.step_index > 0 && res.data && Object.keys(res.data).length > 0) {
          const merged = {
            writer_type: '',
            book_type: '',
            writing_mode: '',
            writing_goals: '',
            target_timeline: '',
            writing_schedule: '',
            accountability_style: '',
            ai_comfort_level: 'moderate',
            genre_topic: '',
            guidance_mode: 'guided',
            ...res.data,
          } as OnboardingData;
          setStepIndex(res.step_index);
          setData(merged);
          saveProgress(res.step_index, merged);
        }
      })
      .catch(() => {});
  }, []);

  const saveProgressCallback = useCallback(() => {
    saveProgress(stepIndex, data);
  }, [stepIndex, data]);

  useEffect(() => {
    if (stepIndex > 0 && stepIndex < STEPS.length - 1) {
      saveProgressCallback();
    }
  }, [stepIndex, data, saveProgressCallback]);

  const currentStep = STEPS[stepIndex];
  const totalSteps = STEPS.length;
  const progress = ((stepIndex + 1) / totalSteps) * 100;

  const canProceed = () => {
    switch (currentStep.id) {
      case 'welcome':
        return true;
      case 'writer_type':
        return !!data.writer_type;
      case 'book_type':
        return !!data.book_type;
      case 'guidance':
        return !!data.guidance_mode;
      case 'work_style':
        return !!data.writing_mode;
      case 'pace':
        return true;
      case 'complete':
        return true;
      default:
        return false;
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      await api<{ journey_id: string; current_phase: string }>('/api/v1/journey/onboarding', {
        method: 'POST',
        body: JSON.stringify({
          book_type: data.book_type || 'fiction',
          writing_mode: data.writing_mode || 'solo',
          writer_type: data.writer_type || null,
          guidance_mode: data.guidance_mode || 'guided',
          writing_goals: data.writing_goals || null,
          target_timeline: data.target_timeline || null,
          writing_schedule: data.writing_schedule || null,
          accountability_style: data.accountability_style || null,
          ai_comfort_level: data.ai_comfort_level || null,
          genre_topic: data.genre_topic || null,
        }),
      });
      await api('/api/v1/auth/me/preferences', {
        method: 'PATCH',
        body: JSON.stringify({
          preferences: {
            onboarding_completed: true,
            onboarding_writer_type: data.writer_type,
            onboarding_guidance_mode: data.guidance_mode,
            onboarding_progress: null,
          },
        }),
      });
      if (data.accountability_style && data.accountability_style !== 'none') {
        const styleMap: Record<string, string> = {
          gentle: 'gentle',
          structured: 'structured',
          buddy: 'coach',
        };
        const accStyle = styleMap[data.accountability_style] || 'gentle';
        try {
          await api('/api/v1/accountability/settings', {
            method: 'PATCH',
            body: JSON.stringify({
              accountability_style: accStyle,
              reminder_enabled: true,
            }),
          });
        } catch {
          /* non-blocking */
        }
      } else if (data.accountability_style === 'none') {
        try {
          await api('/api/v1/accountability/settings', {
            method: 'PATCH',
            body: JSON.stringify({ reminder_enabled: false }),
          });
        } catch {
          /* non-blocking */
        }
      }
      clearProgress();
      router.push('/dashboard/projects/new');
    } catch (e) {
      console.error(e);
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (currentStep.id === 'complete') {
      handleSubmit();
      return;
    }
    const nextIdx = stepIndex + 1;
    saveProgress(nextIdx, data);
    api('/api/v1/journey/onboarding/progress', {
      method: 'POST',
      body: JSON.stringify({ step_index: nextIdx, data }),
    }).catch(() => {});
    if (nextIdx < totalSteps) setStepIndex(nextIdx);
  };

  const handleBack = () => {
    if (stepIndex > 0) setStepIndex(stepIndex - 1);
  };

  const Icon = currentStep.icon;

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
            <Progress value={progress} showLabel size="sm" className="mb-4" />
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-2">
              <Icon className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-serif">{currentStep.title}</CardTitle>
            <CardDescription className="text-base">
              {currentStep.id === 'welcome' && ONBOARDING_WELCOME.description}
              {currentStep.id === 'writer_type' && WRITER_TYPES.subheading}
              {currentStep.id === 'book_type' && PROJECT_TYPE_STEP.subheading}
              {currentStep.id === 'guidance' && GUIDANCE_STEP.subheading}
              {currentStep.id === 'work_style' && WORK_STYLE_STEP.subheading}
              {currentStep.id === 'pace' && PACE_STEP.subheading}
              {currentStep.id === 'complete' && COMPLETE_STEP.description}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {currentStep.id === 'welcome' && (
              <div className="space-y-4">
                <p className="text-muted-foreground">
                  Your writing sanctuary awaits. Let&apos;s set you up for success.
                </p>
              </div>
            )}

            {currentStep.id === 'writer_type' && (
              <div className="grid gap-3 sm:grid-cols-2">
                {WRITER_TYPE_OPTIONS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, writer_type: opt.id }))}
                    className={`rounded-lg border p-4 text-left transition-colors ${
                      data.writer_type === opt.id
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <span className="font-medium">{opt.label}</span>
                    <p className="text-sm text-muted-foreground mt-1">{opt.desc}</p>
                  </button>
                ))}
              </div>
            )}

            {currentStep.id === 'book_type' && (
              <div className="grid gap-3 sm:grid-cols-2">
                <button
                  type="button"
                  onClick={() => setData((d) => ({ ...d, book_type: 'fiction' }))}
                  className={`rounded-lg border p-4 text-left transition-colors ${
                    data.book_type === 'fiction'
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <span className="font-medium">{PROJECT_TYPE_STEP.fiction}</span>
                  <p className="text-sm text-muted-foreground mt-1">{PROJECT_TYPE_STEP.fictionDesc}</p>
                </button>
                <button
                  type="button"
                  onClick={() => setData((d) => ({ ...d, book_type: 'nonfiction' }))}
                  className={`rounded-lg border p-4 text-left transition-colors ${
                    data.book_type === 'nonfiction'
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                >
                  <span className="font-medium">{PROJECT_TYPE_STEP.nonfiction}</span>
                  <p className="text-sm text-muted-foreground mt-1">{PROJECT_TYPE_STEP.nonfictionDesc}</p>
                </button>
              </div>
            )}

            {currentStep.id === 'guidance' && (
              <div className="space-y-3">
                <p className="text-xs text-muted-foreground">{GUIDANCE_STEP.noneWrong}</p>
                <div className="grid gap-3">
                  {(['guided', 'flexible', 'freeform'] as const).map((m) => (
                    <button
                      key={m}
                      type="button"
                      onClick={() => setData((d) => ({ ...d, guidance_mode: m }))}
                      className={`rounded-lg border p-4 text-left transition-colors ${
                        data.guidance_mode === m
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <span className="font-medium">{GUIDANCE_STEP[m].label}</span>
                      <p className="text-sm text-muted-foreground mt-1">{GUIDANCE_STEP[m].desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {currentStep.id === 'work_style' && (
              <div className="grid gap-3">
                {[
                  { id: 'solo', label: WORK_STYLE_STEP.solo.label, desc: WORK_STYLE_STEP.solo.desc, icon: User },
                  { id: 'cowrite', label: WORK_STYLE_STEP.cowrite.label, desc: WORK_STYLE_STEP.cowrite.desc, icon: PenLine },
                  { id: 'ghostwriter', label: WORK_STYLE_STEP.ghostwriter.label, desc: WORK_STYLE_STEP.ghostwriter.desc, icon: Bot },
                ].map((opt) => {
                  const ModeIcon = opt.icon;
                  return (
                    <button
                      key={opt.id}
                      type="button"
                      onClick={() => setData((d) => ({ ...d, writing_mode: opt.id }))}
                      className={`flex items-start gap-3 rounded-lg border p-4 text-left transition-colors ${
                        data.writing_mode === opt.id
                          ? 'border-primary bg-primary/5'
                          : 'border-border hover:border-primary/50'
                      }`}
                    >
                      <ModeIcon className="h-5 w-5 mt-0.5 text-primary shrink-0" />
                      <div>
                        <span className="font-medium">{opt.label}</span>
                        <p className="text-sm text-muted-foreground mt-1">{opt.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {currentStep.id === 'pace' && (
              <div className="space-y-6">
                <div>
                  <Label className="text-sm font-medium">{PACE_STEP.timeline}</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {TIMELINE_OPTIONS.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => setData((d) => ({ ...d, target_timeline: opt.id }))}
                        className={`rounded-full px-4 py-2 text-sm transition-colors ${
                          data.target_timeline === opt.id
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted hover:bg-muted/80'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">{PACE_STEP.schedule}</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {SCHEDULE_OPTIONS.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => setData((d) => ({ ...d, writing_schedule: opt.id }))}
                        className={`rounded-full px-4 py-2 text-sm transition-colors ${
                          data.writing_schedule === opt.id
                            ? 'bg-primary text-primary-foreground'
                            : 'bg-muted hover:bg-muted/80'
                        }`}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <Label className="text-sm font-medium">{PACE_STEP.accountability}</Label>
                  <div className="grid gap-2 sm:grid-cols-2 mt-2">
                    {ACCOUNTABILITY_OPTIONS.map((opt) => (
                      <button
                        key={opt.id}
                        type="button"
                        onClick={() => setData((d) => ({ ...d, accountability_style: opt.id }))}
                        className={`rounded-lg border p-3 text-left transition-colors ${
                          data.accountability_style === opt.id
                            ? 'border-primary bg-primary/5'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <span className="font-medium text-sm">{opt.label}</span>
                        <p className="text-xs text-muted-foreground mt-0.5">{opt.desc}</p>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {currentStep.id === 'complete' && (
              <div className="rounded-lg bg-muted/50 p-4 space-y-2 text-sm">
                <p>
                  <strong>Book type:</strong> {data.book_type === 'fiction' ? 'Fiction' : 'Non-fiction'}
                </p>
                <p>
                  <strong>Mode:</strong>{' '}
                  {data.writing_mode === 'solo'
                    ? 'Write myself'
                    : data.writing_mode === 'cowrite'
                      ? 'Co-write with AI'
                      : 'Ghostwriter'}
                </p>
                <p>
                  <strong>Guidance:</strong> {data.guidance_mode.charAt(0).toUpperCase() + data.guidance_mode.slice(1)}
                </p>
                <p className="text-muted-foreground pt-2">
                  Your personalized roadmap will guide you from idea to finished book.
                </p>
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
                ) : currentStep.id === 'complete' ? (
                  <Check className="h-4 w-4 mr-2" />
                ) : (
                  <ChevronRight className="h-4 w-4 mr-2" />
                )}
                {currentStep.id === 'complete'
                  ? submitting
                    ? 'Creating your journey...'
                    : COMPLETE_STEP.cta
                  : 'Continue'}
              </Button>
              {stepIndex > 0 && (
                <Button variant="ghost" onClick={handleBack} disabled={submitting}>
                  <ChevronLeft className="h-4 w-4 mr-1" />
                  Back
                </Button>
              )}
              {currentStep.id !== 'welcome' && currentStep.id !== 'complete' && (
                <Button variant="link" asChild>
                  <Link href="/dashboard">{ONBOARDING_SKIP.skip}</Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
