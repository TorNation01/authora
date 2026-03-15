'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  const [workspace, setWorkspace] = useState<GhostwriterWorkspace | null>(null);
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState('heavy');
  const [voiceTone, setVoiceTone] = useState('');
  const [targetAudience, setTargetAudience] = useState('');
  const [desiredOutcome, setDesiredOutcome] = useState('');
  const [topic, setTopic] = useState('');
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
    Promise.all([fetchWorkspace(), fetchBook()]).finally(() => setLoading(false));
  }, [fetchWorkspace, fetchBook]);

  useEffect(() => {
    if (workspace) {
      setMode(workspace.mode || 'heavy');
      setVoiceTone(workspace.voice_tone || '');
      setTargetAudience(workspace.target_audience || '');
      setDesiredOutcome(workspace.desired_outcome || '');
    }
  }, [workspace?.id]);

  const handleSubmitIntake = async () => {
    setLoading(true);
    try {
      const ws = await api<GhostwriterWorkspace>(`/api/v1/projects/${projectId}/books/${bookId}/ghostwriter/intake`, {
        method: 'POST',
        body: JSON.stringify({
          mode,
          intake_answers: { topic: topic || undefined },
          voice_tone: voiceTone || undefined,
          target_audience: targetAudience || undefined,
          desired_outcome: desiredOutcome || undefined,
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
      toast({ title: 'Generation failed', description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
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
      toast({ title: 'Generation failed', description: e instanceof Error ? e.message : 'Please try again.', variant: 'destructive' });
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
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Mode</Label>
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
          <div>
            <Label htmlFor="topic">Topic / premise</Label>
            <Input id="topic" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="What is your book about?" className="mt-1" />
          </div>
          <div>
            <Label htmlFor="voice">Voice & tone</Label>
            <Input id="voice" value={voiceTone} onChange={(e) => setVoiceTone(e.target.value)} placeholder="e.g. Conversational, authoritative, warm" className="mt-1" />
          </div>
          <div>
            <Label htmlFor="audience">Target audience</Label>
            <Input id="audience" value={targetAudience} onChange={(e) => setTargetAudience(e.target.value)} placeholder="Who is this book for?" className="mt-1" />
          </div>
          <div>
            <Label htmlFor="outcome">Desired outcome</Label>
            <Input id="outcome" value={desiredOutcome} onChange={(e) => setDesiredOutcome(e.target.value)} placeholder="What should readers gain?" className="mt-1" />
          </div>
          <Button onClick={handleSubmitIntake} disabled={loading}>
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4" />}
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
