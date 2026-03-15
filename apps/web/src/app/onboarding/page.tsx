'use client';

import { useEffect, useState } from 'react';
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
} from 'lucide-react';

interface OnboardingData {
  book_type: string;
  writing_mode: string;
  writing_goals: string;
  target_timeline: string;
  writing_schedule: string;
  accountability_style: string;
  ai_comfort_level: string;
  genre_topic: string;
}

const STEPS = [
  { id: 'welcome', title: 'Welcome', icon: BookOpen },
  { id: 'book_type', title: 'What are you writing?', icon: BookOpen },
  { id: 'writing_mode', title: 'How would you like to write?', icon: PenLine },
  { id: 'writing_goals', title: 'What matters most?', icon: Target },
  { id: 'target_timeline', title: 'When do you hope to finish?', icon: Calendar },
  { id: 'writing_schedule', title: 'When do you usually write?', icon: Clock },
  { id: 'accountability', title: 'How do you like to be encouraged?', icon: Heart },
  { id: 'ai_comfort', title: 'How much AI help?', icon: Sparkles },
  { id: 'genre', title: 'Genre or topic', icon: BookOpen },
  { id: 'complete', title: "You're all set", icon: Check },
];

const BOOK_TYPES = [
  { id: 'fiction', label: 'Fiction', desc: 'Novels, stories, creative writing' },
  { id: 'nonfiction', label: 'Non-fiction', desc: 'Memoir, how-to, business, academic' },
];

const WRITING_MODES = [
  { id: 'solo', label: 'Mostly on my own', desc: 'I write; AI helps when I ask', icon: User },
  { id: 'cowrite', label: 'Co-write with AI', desc: 'AI suggests and drafts; I edit and steer', icon: PenLine },
  { id: 'ghostwriter', label: 'Heavy AI assistance', desc: 'AI drafts; I guide and refine', icon: Bot },
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
  { id: 'gentle', label: 'Gentle', desc: 'Soft reminders, no pressure' },
  { id: 'structured', label: 'Structured', desc: 'Clear goals and check-ins' },
  { id: 'buddy', label: 'Buddy', desc: 'Community and encouragement' },
];

const AI_COMFORT_OPTIONS = [
  { id: 'minimal', label: 'Minimal', desc: 'Only when I ask' },
  { id: 'moderate', label: 'Moderate', desc: 'Suggestions and prompts' },
  { id: 'full', label: 'Full', desc: 'Drafting, rewriting, expansion' },
];

export default function OnboardingPage() {
  const [stepIndex, setStepIndex] = useState(0);
  const [data, setData] = useState<OnboardingData>({
    book_type: '',
    writing_mode: '',
    writing_goals: '',
    target_timeline: '',
    writing_schedule: '',
    accountability_style: '',
    ai_comfort_level: '',
    genre_topic: '',
  });
  const [submitting, setSubmitting] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (!localStorage.getItem('access_token')) {
      router.replace('/login');
    }
  }, [router]);

  const currentStep = STEPS[stepIndex];
  const totalSteps = STEPS.length;
  const progress = ((stepIndex + 1) / totalSteps) * 100;

  const canProceed = () => {
    switch (currentStep.id) {
      case 'welcome':
        return true;
      case 'book_type':
        return !!data.book_type;
      case 'writing_mode':
        return !!data.writing_mode;
      case 'writing_goals':
        return !!data.writing_goals.trim();
      case 'target_timeline':
        return !!data.target_timeline;
      case 'writing_schedule':
        return !!data.writing_schedule;
      case 'accountability':
        return !!data.accountability_style;
      case 'ai_comfort':
        return !!data.ai_comfort_level;
      case 'genre':
        return !!data.genre_topic.trim();
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
          writing_goals: data.writing_goals || null,
          target_timeline: data.target_timeline || null,
          writing_schedule: data.writing_schedule || null,
          accountability_style: data.accountability_style || null,
          ai_comfort_level: data.ai_comfort_level || null,
          genre_topic: data.genre_topic || null,
        }),
      });
      router.push('/dashboard');
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
    if (stepIndex < totalSteps - 1) setStepIndex(stepIndex + 1);
  };

  const handleBack = () => {
    if (stepIndex > 0) setStepIndex(stepIndex - 1);
  };

  const Icon = currentStep.icon;

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background p-4">
      <div className="w-full max-w-xl">
        <Link
          href="/dashboard"
          className="mb-8 inline-block font-serif text-xl font-bold text-foreground hover:text-primary transition-colors"
        >
          AUTHORA
        </Link>
        <Card variant="sanctuary">
          <CardHeader>
            <Progress value={progress} showLabel size="sm" className="mb-4" />
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-2">
              <Icon className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-serif">{currentStep.title}</CardTitle>
            <CardDescription className="text-base">
              {currentStep.id === 'welcome' &&
                "We'll ask a few quick questions to personalize your experience. You can change these anytime."}
              {currentStep.id === 'book_type' && 'This helps us show you the right tools and structure.'}
              {currentStep.id === 'writing_mode' && 'Choose the level of AI help that feels right.'}
              {currentStep.id === 'writing_goals' && "What's your main goal for this book?"}
              {currentStep.id === 'target_timeline' && 'No pressure—this helps us suggest a pace.'}
              {currentStep.id === 'writing_schedule' && "We'll use this for gentle reminders—only if you want them."}
              {currentStep.id === 'accountability' && 'We adapt to your style. No guilt, ever.'}
              {currentStep.id === 'ai_comfort' && 'You can change this anytime in settings.'}
              {currentStep.id === 'genre' && 'e.g. romance, thriller, memoir, business.'}
              {currentStep.id === 'complete' && "Your journey begins now. Create a project and add your first book."}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {currentStep.id === 'welcome' && (
              <p className="text-muted-foreground">
                Your writing sanctuary awaits. Let&apos;s set you up for success.
              </p>
            )}

            {currentStep.id === 'book_type' && (
              <div className="grid gap-3 sm:grid-cols-2">
                {BOOK_TYPES.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, book_type: opt.id }))}
                    className={`rounded-lg border p-4 text-left transition-colors ${
                      data.book_type === opt.id
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

            {currentStep.id === 'writing_mode' && (
              <div className="grid gap-3">
                {WRITING_MODES.map((opt) => {
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
                      <ModeIcon className="h-5 w-5 mt-0.5 text-primary" />
                      <div>
                        <span className="font-medium">{opt.label}</span>
                        <p className="text-sm text-muted-foreground mt-1">{opt.desc}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {currentStep.id === 'writing_goals' && (
              <div className="space-y-2">
                <Label htmlFor="goals">What do you want to achieve?</Label>
                <Input
                  id="goals"
                  placeholder="e.g. Finish my first draft, publish by summer, build a habit..."
                  value={data.writing_goals}
                  onChange={(e) => setData((d) => ({ ...d, writing_goals: e.target.value }))}
                  className="min-h-[80px]"
                />
              </div>
            )}

            {currentStep.id === 'target_timeline' && (
              <div className="flex flex-wrap gap-2">
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
            )}

            {currentStep.id === 'writing_schedule' && (
              <div className="flex flex-wrap gap-2">
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
            )}

            {currentStep.id === 'accountability' && (
              <div className="grid gap-3">
                {ACCOUNTABILITY_OPTIONS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, accountability_style: opt.id }))}
                    className={`rounded-lg border p-4 text-left transition-colors ${
                      data.accountability_style === opt.id
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

            {currentStep.id === 'ai_comfort' && (
              <div className="grid gap-3">
                {AI_COMFORT_OPTIONS.map((opt) => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setData((d) => ({ ...d, ai_comfort_level: opt.id }))}
                    className={`rounded-lg border p-4 text-left transition-colors ${
                      data.ai_comfort_level === opt.id
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

            {currentStep.id === 'genre' && (
              <div className="space-y-2">
                <Label htmlFor="genre">Genre or topic</Label>
                <Input
                  id="genre"
                  placeholder="e.g. Thriller, memoir, business, self-help..."
                  value={data.genre_topic}
                  onChange={(e) => setData((d) => ({ ...d, genre_topic: e.target.value }))}
                />
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
                {data.genre_topic && (
                  <p>
                    <strong>Genre:</strong> {data.genre_topic}
                  </p>
                )}
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
                ) : null}
                {currentStep.id === 'complete'
                  ? submitting
                    ? 'Creating your journey...'
                    : 'Start my journey'
                  : 'Continue'}
              </Button>
              {stepIndex > 0 && (
                <Button variant="ghost" onClick={handleBack} disabled={submitting}>
                  Back
                </Button>
              )}
              {currentStep.id !== 'welcome' && currentStep.id !== 'complete' && (
                <Button variant="link" asChild>
                  <Link href="/dashboard">Skip</Link>
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
