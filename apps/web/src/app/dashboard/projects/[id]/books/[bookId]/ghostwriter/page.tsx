'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { getBillingStatus, canUseFeature } from '@/lib/billing';
import { useUpgradeTrigger } from '@/contexts/UpgradeTriggerContext';
import { useConfig } from '@/contexts/ConfigProvider';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  Sparkles,
  ChevronLeft,
  Loader2,
  Check,
  PenLine,
  FileText,
  List,
  Bot,
  User,
  Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface GhostwriterWorkspace {
  id: string;
  book_id: string;
  mode: string;
  workflow_step: string;
  intake_answers: Record<string, string> | null;
  voice_tone: string | null;
  target_audience: string | null;
  desired_outcome: string | null;
  word_count_target: string | null;
  deadline: string | null;
  author_background: string | null;
  sample_text: string | null;
  content_warnings: string | null;
  research_notes: string | null;
  outline: { chapters?: Array<{ title: string; summary: string }> } | null;
  outline_approved_at: string | null;
  chapter_briefs: Array<{ id: string; chapter_id: string; brief_text: string; approved_at: string | null }>;
}

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  content_source?: string | null;
}

interface Book {
  id: string;
  title: string;
  type: string;
  chapters: Chapter[];
}

const MODES = [
  { id: 'light', label: 'Light ghostwriting', desc: 'AI assists with sections; you write most of it', icon: PenLine },
  { id: 'heavy', label: 'Heavy ghostwriting', desc: 'AI drafts chapters from your briefs; you edit and approve', icon: Bot },
  { id: 'full', label: 'Full guided draft', desc: 'AI generates full draft from outline; you review and refine', icon: Zap },
];

export default function GhostwriterPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const { toast } = useToast();
  const config = useConfig();
  const { showUpgrade } = useUpgradeTrigger();
  const [workspace, setWorkspace] = useState<GhostwriterWorkspace | null>(null);
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState('heavy');
  // Intake fields — all stored in intake_answers JSONB for unlimited length
  const [topic, setTopic] = useState('');
  const [voiceTone, setVoiceTone] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [desiredOutcome, setDesiredOutcome] = useState('');
  const [genre, setGenre] = useState('');
  const [comparableTitles, setComparableTitles] = useState('');
  const [protagonistSummary, setProtagonistSummary] = useState('');
  const [antagonistConflict, setAntagonistConflict] = useState('');
  const [settingWorld, setSettingWorld] = useState('');
  const [themesMotifs, setThemesMotifs] = useState('');
  const [narrativeStyle, setNarrativeStyle] = useState('');
  const [pacingPreference, setPacingPreference] = useState('');
  const [keyScenes, setKeyScenes] = useState('');
  const [seriesPotential, setSeriesPotential] = useState('');
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [wordCountTarget, setWordCountTarget] = useState('');
  const [deadline, setDeadline] = useState('');
  const [authorBackground, setAuthorBackground] = useState('');
  const [sampleText, setSampleText] = useState('');
  const [contentWarnings, setContentWarnings] = useState('');
  const [researchNotes, setResearchNotes] = useState('');
  const [generatingOutline, setGeneratingOutline] = useState(false);
  const [generatingBrief, setGeneratingBrief] = useState<string | null>(null);
  const [generatingDraft, setGeneratingDraft] = useState<string | null>(null);
  const [selectedChapterForDraft, setSelectedChapterForDraft] = useState<string | null>(null);
  const [draftPreview, setDraftPreview] = useState<{ chapterId: string; text: string } | null>(null);

  const fetchWorkspace = useCallback(() => {
    api<GhostwriterWorkspace>(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter`)
      .then(setWorkspace)
      .catch(() => setWorkspace(null));
  }, [projectId, bookId]);

  const fetchBook = useCallback(() => {
    api<Book>(`/api/v1/projects/${projectId}/books/${bookId}`)
      .then(setBook)
      .catch(() => router.push('/dashboard'));
  }, [projectId, bookId, router]);

  useEffect(() => {
    if (!config.feature_flags.billing) {
      Promise.all([fetchWorkspace(), fetchBook()]).finally(() => setLoading(false));
      return;
    }
    getBillingStatus().then((status) => {
      if (!canUseFeature(status, 'ghostwriter')) {
        showUpgrade('feature_locked', { featureLabel: 'Ghostwriter' });
        router.replace(`/dashboard/projects/${projectId}/books/${bookId}`);
        setLoading(false);
        return;
      }
      Promise.all([fetchWorkspace(), fetchBook()]).finally(() => setLoading(false));
    });
  }, [config.feature_flags.billing, fetchWorkspace, fetchBook, projectId, bookId, router, showUpgrade]);

  useEffect(() => {
    if (workspace) {
      setMode(workspace.mode || 'heavy');
      setVoiceTone(workspace.voice_tone || '');
      setTargetAudience(workspace.target_audience || '');
      setDesiredOutcome(workspace.desired_outcome || '');
      const ia = workspace.intake_answers || {};
      setTopic(ia.topic || '');
      setGenre(ia.genre || '');
      setComparableTitles(ia.comparable_titles || '');
      setProtagonistSummary(ia.protagonist_summary || '');
      setAntagonistConflict(ia.antagonist_conflict || '');
      setSettingWorld(ia.setting_world || '');
      setThemesMotifs(ia.themes_motifs || '');
      setNarrativeStyle(ia.narrative_style || '');
      setPacingPreference(ia.pacing_preference || '');
      setKeyScenes(ia.key_scenes || '');
      setSeriesPotential(ia.series_potential || '');
      setAdditionalNotes(ia.additional_notes || '');
      setWordCountTarget(workspace.word_count_target || '');
      setDeadline(workspace.deadline || '');
      setAuthorBackground(workspace.author_background || '');
      setSampleText(workspace.sample_text || '');
      setContentWarnings(workspace.content_warnings || '');
      setResearchNotes(workspace.research_notes || '');
    }
  }, [workspace?.id]);

  const handleSubmitIntake = async () => {
    setLoading(true);
    try {
      const ws = await api<GhostwriterWorkspace>(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/intake`, {
        method: 'POST',
        body: JSON.stringify({
          mode,
          intake_answers: {
            topic: topic || undefined,
            genre: genre || undefined,
            comparable_titles: comparableTitles || undefined,
            protagonist_summary: protagonistSummary || undefined,
            antagonist_conflict: antagonistConflict || undefined,
            setting_world: settingWorld || undefined,
            themes_motifs: themesMotifs || undefined,
            narrative_style: narrativeStyle || undefined,
            pacing_preference: pacingPreference || undefined,
            key_scenes: keyScenes || undefined,
            series_potential: seriesPotential || undefined,
            additional_notes: additionalNotes || undefined,
          },
          voice_tone: voiceTone || undefined,
          target_audience: targetAudience || undefined,
          desired_outcome: desiredOutcome || undefined,
          word_count_target: wordCountTarget || undefined,
          deadline: deadline || undefined,
          author_background: authorBackground || undefined,
          sample_text: sampleText || undefined,
          content_warnings: contentWarnings || undefined,
          research_notes: researchNotes || undefined,
        }),
      });
      setWorkspace(ws);
      toast({ title: 'Intake saved' });
    } catch (e) {
      toast({ title: 'Failed', description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateOutline = async () => {
    setGeneratingOutline(true);
    try {
      const { outline } = await api<{ outline: GhostwriterWorkspace['outline'] }>(
        `/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/outline/generate`,
        { method: 'POST' }
      );
      setWorkspace((w) => (w ? { ...w, outline } : null));
      toast({ title: 'Outline generated' });
    } catch (e) {
      toast({ title: "Generation didn't complete", description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setGeneratingOutline(false);
    }
  };

  const handleApproveOutline = async () => {
    if (!workspace?.outline) return;
    setLoading(true);
    try {
      const ws = await api<GhostwriterWorkspace>(
        `/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/outline/approve`,
        { method: 'POST', body: JSON.stringify({ outline: workspace.outline }) }
      );
      setWorkspace(ws);
      fetchBook();
      toast({ title: 'Outline approved' });
    } catch (e) {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBrief = async (chapterId: string) => {
    setGeneratingBrief(chapterId);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/briefs/${chapterId}/generate`, {
        method: 'POST',
      });
      fetchWorkspace();
      toast({ title: 'Brief generated' });
    } catch (e) {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setGeneratingBrief(null);
    }
  };

  const handleApproveBrief = async (chapterId: string) => {
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/briefs/${chapterId}/approve`, {
        method: 'POST',
      });
      fetchWorkspace();
      toast({ title: 'Brief approved' });
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    }
  };

  const handleGenerateDraft = async (chapterId: string) => {
    setGeneratingDraft(chapterId);
    setDraftPreview(null);
    try {
      const { draft_text } = await api<{ draft_text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/draft/generate`,
        { method: 'POST', body: JSON.stringify({ chapter_id: chapterId, use_brief: true }) }
      );
      setDraftPreview({ chapterId, text: draft_text });
      setSelectedChapterForDraft(chapterId);
    } catch (e) {
      toast({ title: "Generation didn't complete", description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
    } finally {
      setGeneratingDraft(null);
    }
  };

  const handleApplyDraft = async () => {
    if (!draftPreview) return;
    setLoading(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/draft/apply`, {
        method: 'POST',
        body: JSON.stringify({ chapter_id: draftPreview.chapterId, draft_text: draftPreview.text }),
      });
      setDraftPreview(null);
      setSelectedChapterForDraft(null);
      fetchBook();
      toast({ title: 'Draft applied', description: 'Content marked as AI-generated.' });
    } catch (e) {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const chapters = [...(book?.chapters ?? [])].sort((a, b) => a.sort_order - b.sort_order);
  const getBrief = (chapterId: string) => workspace?.chapter_briefs?.find((b) => b.chapter_id === chapterId);

  if (loading && !workspace) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
          <Button variant="ghost" size="sm">
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back to manuscript
          </Button>
        </Link>
      </div>

      <PageHeader
        title="Ghostwriter mode"
        description="Create your book with AI-guided drafting. Choose your level of involvement."
        backHref={`/dashboard/projects/${projectId}/books/${bookId}`}
        backLabel="Manuscript"
      />

      {/* Step 1: Intake */}
      <Card variant="soft" className="mb-6">
        <CardHeader>
          <h3 className="font-semibold flex items-center gap-2">
            <List className="h-4 w-4" />
            Step 1: Intake
          </h3>
          <p className="text-sm text-muted-foreground">
            The more detail you provide, the better the AI can craft your book. All fields support up to 50,000 characters — be as thorough as you want.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">
          {/* Mode selection */}
          <div>
            <Label>Ghostwriting mode</Label>
            <div className="grid grid-cols-3 gap-3 mt-2">
              {MODES.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => setMode(m.id)}
                  className={cn(
                    'p-4 rounded-lg border text-left transition-colors',
                    mode === m.id ? 'border-primary bg-primary/5' : 'border-border hover:bg-muted/50'
                  )}
                >
                  <m.icon className="h-5 w-5 mb-2" />
                  <p className="font-medium text-sm">{m.label}</p>
                  <p className="text-xs text-muted-foreground mt-1">{m.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Core concept */}
          <div>
            <Label htmlFor="topic">Topic / premise *</Label>
            <p className="text-xs text-muted-foreground mb-1">What is your book about? Describe the core concept, hook, and central conflict or thesis. The AI uses this as the foundation for everything.</p>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g. A disgraced archaeologist discovers an ancient map leading to a lost civilization beneath Antarctica — but a shadow organization will kill to keep it buried. Or: A practical guide to building wealth through micro-investing for people who think they don't earn enough to start."
              className="min-h-[120px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm font-serif placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Genre */}
          <div>
            <Label htmlFor="genre">Genre / category</Label>
            <p className="text-xs text-muted-foreground mb-1">Primary genre, sub-genres, and any genre-blending elements. e.g. "Science fiction thriller with elements of cosmic horror and political drama"</p>
            <textarea
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              placeholder="e.g. Epic fantasy, psychological thriller, literary fiction, self-help/business, memoir..."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Comparable titles */}
          <div>
            <Label htmlFor="comparable">Comparable titles / inspiration</Label>
            <p className="text-xs text-muted-foreground mb-1">Books, films, or series that capture the feel, tone, or structure you're aiming for. Helps the AI understand your vision.</p>
            <textarea
              id="comparable"
              value={comparableTitles}
              onChange={(e) => setComparableTitles(e.target.value)}
              placeholder="e.g. 'The tone of The Name of the Wind meets the pacing of The Da Vinci Code' or 'Similar to Atomic Habits but focused on creative professionals'"
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Voice & tone */}
          <div>
            <Label htmlFor="voice">Voice & tone</Label>
            <p className="text-xs text-muted-foreground mb-1">The narrative voice, emotional register, and stylistic approach. Be specific — this shapes every sentence the AI writes.</p>
            <textarea
              id="voice"
              value={voiceTone}
              onChange={(e) => setVoiceTone(e.target.value)}
              placeholder="e.g. First-person, intimate and confessional, with dark humor. Or: Third-person omniscient, lyrical and atmospheric, reminiscent of literary fiction. Or: Direct, authoritative, and encouraging — like a trusted mentor."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Target audience */}
          <div>
            <Label htmlFor="audience">Target audience</Label>
            <p className="text-xs text-muted-foreground mb-1">Who are you writing for? Demographics, reading level, interests, what they already know, what they need explained.</p>
            <textarea
              id="audience"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              placeholder="e.g. Adult fantasy readers who love complex worldbuilding, ages 25-45, familiar with Sanderson and Hobb. Or: First-time entrepreneurs who've never read a business book, need everything explained simply."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Desired outcome */}
          <div>
            <Label htmlFor="outcome">Desired outcome</Label>
            <p className="text-xs text-muted-foreground mb-1">What should readers feel, think, or do after finishing? The emotional and practical impact you want to create.</p>
            <textarea
              id="outcome"
              value={desiredOutcome}
              onChange={(e) => setDesiredOutcome(e.target.value)}
              placeholder="e.g. Readers should feel they've lived another life, with a lingering sense of wonder and loss. Or: Readers should walk away with a clear, actionable 30-day plan and the confidence to execute it."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Protagonist / main character */}
          <div>
            <Label htmlFor="protagonist">Protagonist / main character(s)</Label>
            <p className="text-xs text-muted-foreground mb-1">Who is the story about? Personality, background, flaws, desires, arc. For nonfiction: who is the guide/author persona?</p>
            <textarea
              id="protagonist"
              value={protagonistSummary}
              onChange={(e) => setProtagonistSummary(e.target.value)}
              placeholder="e.g. Dr. Elena Voss, 38, brilliant but haunted by a failed expedition that cost her team their lives. She's driven by guilt and a need for redemption, but her obsession blinds her to the people who care about her now."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Antagonist / conflict */}
          <div>
            <Label htmlFor="antagonist">Antagonist / central conflict</Label>
            <p className="text-xs text-muted-foreground mb-1">Who or what opposes the protagonist? The nature of the conflict — internal, external, systemic. What's at stake?</p>
            <textarea
              id="antagonist"
              value={antagonistConflict}
              onChange={(e) => setAntagonistConflict(e.target.value)}
              placeholder="e.g. The Consortium — a centuries-old cabal that has guarded the Antarctic secret since the 1800s. Led by a charismatic zealot who genuinely believes revealing the truth would destroy civilization. The real antagonist is the question: is some knowledge too dangerous to share?"
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Setting / world */}
          <div>
            <Label htmlFor="setting">Setting / world</Label>
            <p className="text-xs text-muted-foreground mb-1">Time period, location(s), world rules (magic system, technology, social structure). The physical and cultural landscape.</p>
            <textarea
              id="setting"
              value={settingWorld}
              onChange={(e) => setSettingWorld(e.target.value)}
              placeholder="e.g. Present day, opening in Cambridge then moving to Antarctica. The hidden city is a blend of Art Deco and alien architecture, powered by geothermal energy and technology that appears magical. Or: Contemporary United States, focused on the gig economy and startup culture."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Themes & motifs */}
          <div>
            <Label htmlFor="themes">Themes & motifs</Label>
            <p className="text-xs text-muted-foreground mb-1">The big ideas your book explores. Recurring symbols, questions, philosophical threads. What is this book really about?</p>
            <textarea
              id="themes"
              value={themesMotifs}
              onChange={(e) => setThemesMotifs(e.target.value)}
              placeholder="e.g. The cost of knowledge, redemption vs. obsession, the tension between scientific truth and public safety. Recurring motif: maps — both literal and metaphorical — and the idea that some territories should remain uncharted."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Narrative style */}
          <div>
            <Label htmlFor="narrative">Narrative style / POV</Label>
            <p className="text-xs text-muted-foreground mb-1">Point of view, tense, chapter structure, any experimental techniques. How the story is told.</p>
            <textarea
              id="narrative"
              value={narrativeStyle}
              onChange={(e) => setNarrativeStyle(e.target.value)}
              placeholder="e.g. Dual timeline — present-day expedition chapters in third-person limited (Elena's POV), interspersed with 1920s journal entries from the original discoverer. Present tense for the expedition, past tense for the historical sections."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Pacing */}
          <div>
            <Label htmlFor="pacing">Pacing preference</Label>
            <p className="text-xs text-muted-foreground mb-1">How should the book feel moment to moment? Fast thriller pace, slow literary burn, or something specific?</p>
            <textarea
              id="pacing"
              value={pacingPreference}
              onChange={(e) => setPacingPreference(e.target.value)}
              placeholder="e.g. Opening with a fast-paced prologue (the original discovery gone wrong), then settling into a steady build with escalating tension. Short chapters (2,000-3,000 words) with cliffhanger endings. Climax should be relentless."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Key scenes */}
          <div>
            <Label htmlFor="scenes">Key scenes / set pieces</Label>
            <p className="text-xs text-muted-foreground mb-1">Specific moments you already have in mind — the scenes that made you want to write this book. The AI will build toward and around these.</p>
            <textarea
              id="scenes"
              value={keyScenes}
              onChange={(e) => setKeyScenes(e.target.value)}
              placeholder="e.g. 1) The moment the ice shelf collapses, revealing the city. 2) A chase through the alien library where the shelves rearrange themselves. 3) The final confrontation in the heart of the geothermal core, where Elena must choose between publishing her findings or destroying them."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Series potential */}
          <div>
            <Label htmlFor="series">Series potential</Label>
            <p className="text-xs text-muted-foreground mb-1">Is this a standalone or part of a series? If a series, describe the arc across books, loose threads to plant, and how this book fits.</p>
            <textarea
              id="series"
              value={seriesPotential}
              onChange={(e) => setSeriesPotential(e.target.value)}
              placeholder="e.g. Book 1 of a planned trilogy. This book ends with the city's discovery becoming public — but the Consortium isn't defeated, just exposed. Book 2 explores the global fallout. Book 3 deals with what else is buried under other continents. Plant hints about the global network in this book."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Additional notes */}
          <div>
            <Label htmlFor="notes">Additional notes / constraints</Label>
            <p className="text-xs text-muted-foreground mb-1">Anything else the AI should know. Content warnings to handle sensitively, things to avoid, specific research to incorporate, word count targets, deadlines.</p>
            <textarea
              id="notes"
              value={additionalNotes}
              onChange={(e) => setAdditionalNotes(e.target.value)}
              placeholder="e.g. Avoid graphic violence — keep it PG-13. The archaeology should be accurate; I've attached research notes. Target 80,000 words. No romance subplot for Elena — she's not in that headspace. The Antarctic setting needs to feel authentic — incorporate real research station details."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Word count target */}
          <div>
            <Label htmlFor="wordCount">Word count target</Label>
            <p className="text-xs text-muted-foreground mb-1">Your target word count for the finished manuscript. Helps the AI plan chapter length and pacing.</p>
            <input
              id="wordCount"
              type="text"
              value={wordCountTarget}
              onChange={(e) => setWordCountTarget(e.target.value)}
              placeholder="e.g. 80,000 or 80k-100k"
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Deadline */}
          <div>
            <Label htmlFor="deadline">Deadline</Label>
            <p className="text-xs text-muted-foreground mb-1">When do you need the manuscript finished? Optional but helps with pacing recommendations.</p>
            <input
              id="deadline"
              type="text"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              placeholder="e.g. December 2026 or 2026-12-31"
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Author background */}
          <div>
            <Label htmlFor="authorBg">Author background</Label>
            <p className="text-xs text-muted-foreground mb-1">Your experience, credentials, or personal connection to the subject. Helps the AI calibrate the authorial voice.</p>
            <textarea
              id="authorBg"
              value={authorBackground}
              onChange={(e) => setAuthorBackground(e.target.value)}
              placeholder="e.g. Former journalist with 10 years covering science and technology. Second novel. Or: Licensed therapist specializing in attachment theory, writing my first book for a general audience."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Sample text */}
          <div>
            <Label htmlFor="sample">Sample text / writing sample</Label>
            <p className="text-xs text-muted-foreground mb-1">Paste a sample of your writing — or writing in the style you want. The AI will match the voice, rhythm, and sentence-level style.</p>
            <textarea
              id="sample"
              value={sampleText}
              onChange={(e) => setSampleText(e.target.value)}
              placeholder="Paste 2-3 paragraphs of your own writing, or a passage from a book whose style you want to emulate..."
              className="min-h-[120px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm font-serif placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Content warnings */}
          <div>
            <Label htmlFor="warnings">Content warnings</Label>
            <p className="text-xs text-muted-foreground mb-1">Sensitive topics your book handles. The AI will treat these with appropriate care and avoid gratuitous treatment.</p>
            <textarea
              id="warnings"
              value={contentWarnings}
              onChange={(e) => setContentWarnings(e.target.value)}
              placeholder="e.g. Violence (non-graphic), psychological trauma, grief, substance abuse (off-screen). Or: None — this is a lighthearted comedy."
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          {/* Research notes */}
          <div>
            <Label htmlFor="research">Research notes</Label>
            <p className="text-xs text-muted-foreground mb-1">Key facts, sources, or domain knowledge the AI should incorporate. Links, references, or summaries of research you've done.</p>
            <textarea
              id="research"
              value={researchNotes}
              onChange={(e) => setResearchNotes(e.target.value)}
              placeholder="e.g. Police procedure in rural jurisdictions — detectives have wide latitude, forensic resources are limited. Key source: 'Rural Policing in America' by Dr. Sarah Chen. Incorporate: the 48-hour rule for missing persons, jurisdictional friction between county and state police."
              className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>

          <Button onClick={handleSubmitIntake} disabled={loading} size="lg" className="w-full">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Check className="h-4 w-4 mr-2" />}
            Save intake
          </Button>
        </CardContent>
      </Card>

      {/* Step 2: Outline */}
      <Card variant="soft" className="mb-6">
        <CardHeader>
          <h3 className="font-semibold flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Step 2: Outline
          </h3>
        </CardHeader>
        <CardContent className="space-y-4">
          {workspace?.outline?.chapters ? (
            <div className="space-y-2">
              {workspace.outline.chapters.map((ch, i) => (
                <div key={i} className="p-3 rounded-lg border bg-background">
                  <p className="font-medium">{ch.title}</p>
                  <p className="text-sm text-muted-foreground">{ch.summary}</p>
                </div>
              ))}
              {!workspace.outline_approved_at ? (
                <div className="flex gap-2">
                  <Button onClick={handleApproveOutline} disabled={loading}>
                    Approve outline
                  </Button>
                  <Button variant="outline" onClick={handleGenerateOutline} disabled={generatingOutline}>
                    {generatingOutline ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Regenerate'}
                  </Button>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Check className="h-4 w-4" />
                  Approved
                </p>
              )}
            </div>
          ) : (
            <Button onClick={handleGenerateOutline} disabled={generatingOutline}>
              {generatingOutline ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Generate outline
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Step 3: Chapter briefs */}
      {workspace?.outline_approved_at && chapters.length > 0 && (
        <Card variant="soft" className="mb-6">
          <CardHeader>
            <h3 className="font-semibold flex items-center gap-2">
              <PenLine className="h-4 w-4" />
              Step 3: Chapter briefs
            </h3>
          </CardHeader>
          <CardContent className="space-y-4">
            {chapters.map((ch) => {
              const brief = getBrief(ch.id);
              return (
                <div key={ch.id} className="p-4 rounded-lg border bg-background">
                  <div className="flex items-center justify-between">
                    <p className="font-medium">{ch.title}</p>
                    <div className="flex gap-2">
                      {brief ? (
                        <>
                          <Button variant="outline" size="sm" onClick={() => handleApproveBrief(ch.id)} disabled={!!brief.approved_at}>
                            {brief.approved_at ? 'Approved' : 'Approve'}
                          </Button>
                          {!brief.approved_at && (
                            <Button size="sm" variant="ghost" onClick={() => handleGenerateBrief(ch.id)} disabled={generatingBrief === ch.id}>
                              {generatingBrief === ch.id ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Regenerate'}
                            </Button>
                          )}
                        </>
                      ) : (
                        <Button size="sm" onClick={() => handleGenerateBrief(ch.id)} disabled={generatingBrief === ch.id}>
                          {generatingBrief === ch.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                          Generate brief
                        </Button>
                      )}
                    </div>
                  </div>
                  {brief && <p className="text-sm text-muted-foreground mt-2 line-clamp-3">{brief.brief_text}</p>}
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      {/* Step 4: Draft generation */}
      {chapters.length > 0 && (
        <Card variant="soft" className="mb-6">
          <CardHeader>
            <h3 className="font-semibold flex items-center gap-2">
              <Bot className="h-4 w-4" />
              Step 4: Generate drafts
            </h3>
            <p className="text-sm text-muted-foreground">
              AI-generated content is clearly marked. User edits update provenance to &quot;AI-assisted&quot;.
            </p>
          </CardHeader>
          <CardContent className="space-y-4">
            {chapters.map((ch) => (
              <div key={ch.id} className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  <span className="font-medium">{ch.title}</span>
                  {ch.content_source && (
                    <span className="text-xs px-2 py-0.5 rounded bg-muted">
                      {ch.content_source === 'ai_generated' ? 'AI draft' : ch.content_source === 'ai_assisted' ? 'AI-assisted' : 'User-written'}
                    </span>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" asChild>
                    <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>Edit</Link>
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleGenerateDraft(ch.id)}
                    disabled={generatingDraft === ch.id || !getBrief(ch.id)?.approved_at}
                  >
                    {generatingDraft === ch.id ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Generate draft'}
                  </Button>
                </div>
              </div>
            ))}
            {draftPreview && (
              <div className="mt-4 p-4 rounded-lg border-2 border-primary/30 bg-primary/5">
                <h4 className="font-medium mb-2">Draft preview</h4>
                <div className="max-h-64 overflow-auto text-sm whitespace-pre-wrap mb-4">{draftPreview.text.slice(0, 2000)}{draftPreview.text.length > 2000 ? '...' : ''}</div>
                <div className="flex gap-2">
                  <Button onClick={handleApplyDraft} disabled={loading}>
                    Apply to chapter
                  </Button>
                  <Button variant="ghost" onClick={() => setDraftPreview(null)}>
                    Cancel
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <p className="text-xs text-muted-foreground">
        Content provenance: <strong>user_written</strong> = you typed it; <strong>ai_assisted</strong> = you edited AI output; <strong>ai_generated</strong> = full AI draft.
      </p>
    </div>
  );
}
