'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';
import { Users } from 'lucide-react';
import { GUIDANCE_MODES } from '@/content/template-copy';
import { SHARING_SETTINGS_CARD } from '@/content/collaboration-copy';

type GuidanceMode = 'guided' | 'flexible' | 'freeform';

interface ProjectData {
  id: string;
  name: string;
  guidance_mode: string;
}

export default function ProjectSettingsPage() {
  const params = useParams();
  const router = useRouter();
  const { toast } = useToast();
  const projectId = params.id as string;
  const [project, setProject] = useState<ProjectData | null>(null);
  const [guidanceMode, setGuidanceMode] = useState<GuidanceMode>('guided');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    api<ProjectData>(`/api/v1/projects/${projectId}`)
      .then((p) => {
        setProject(p);
        setGuidanceMode((p.guidance_mode as GuidanceMode) || 'guided');
      })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [projectId, router]);

  async function handleSave() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}`, {
        method: 'PATCH',
        body: JSON.stringify({ guidance_mode: guidanceMode }),
      });
      toast({ title: 'Settings saved' });
      setProject((p) => (p ? { ...p, guidance_mode: guidanceMode } : null));
    } catch (err) {
      toast({
        title: 'Failed to save',
        description: err instanceof Error ? err.message : 'Try again',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  }

  if (loading || !project) {
    return (
      <div className="p-6 lg:p-8">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="p-6 lg:p-8 max-w-2xl">
      <PageHeader
        title="Project settings"
        description={project.name}
        backHref={`/dashboard/projects/${projectId}`}
        backLabel="Back to project"
      />

      <Link href={`/dashboard/projects/${projectId}/sharing`}>
        <Card variant="sanctuary" className="mt-6 cursor-pointer hover:shadow-md transition-shadow">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="font-serif flex items-center gap-2">
                <Users className="h-5 w-5" />
                {SHARING_SETTINGS_CARD.title}
              </CardTitle>
              <span className="text-sm text-muted-foreground">→</span>
            </div>
            <CardDescription>
              {SHARING_SETTINGS_CARD.description}
            </CardDescription>
          </CardHeader>
        </Card>
      </Link>

      <Card variant="sanctuary" className="mt-6">
        <CardHeader>
          <CardTitle className="font-serif">Genre guidance</CardTitle>
          <CardDescription>
            {GUIDANCE_MODES.subheading} {GUIDANCE_MODES.changeLater}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Guidance mode</Label>
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
          <Button onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save changes'}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
