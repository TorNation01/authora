'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { BookOpen } from 'lucide-react';
import { api } from '@/lib/api';

interface ProjectProgress {
  total_words: number;
  total_chapters: number;
  chapters_done: number;
  progress_pct: number;
  books: Array<{
    id: string;
    title: string;
    word_count: number;
    chapter_count: number;
    chapters_done: number;
  }>;
}

interface ProjectProgressCardProps {
  projectId: string;
  projectName: string;
}

export function ProjectProgressCard({ projectId, projectName }: ProjectProgressCardProps) {
  const [progress, setProgress] = useState<ProjectProgress | null>(null);

  useEffect(() => {
    api<ProjectProgress>(`/api/v1/projects/${projectId}/progress`)
      .then(setProgress)
      .catch(() => setProgress(null));
  }, [projectId]);

  if (!progress || (progress.total_words === 0 && progress.total_chapters === 0)) return null;

  return (
    <Link href={`/dashboard/projects/${projectId}`}>
      <Card variant="sanctuary" className="p-4 transition-colors hover:border-primary/30">
        <div className="flex items-center gap-3 mb-3">
          <BookOpen className="h-5 w-5 text-primary" />
          <h3 className="font-semibold flex-1 truncate">{projectName}</h3>
        </div>
        <div className="grid grid-cols-2 gap-4 mb-3">
          <div>
            <p className="text-2xl font-bold">{progress.total_words.toLocaleString()}</p>
            <p className="text-xs text-muted-foreground">Words</p>
          </div>
          <div>
            <p className="text-2xl font-bold">
              {progress.chapters_done}/{progress.total_chapters}
            </p>
            <p className="text-xs text-muted-foreground">Chapters</p>
          </div>
        </div>
        {progress.total_chapters > 0 && (
          <div>
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>Progress</span>
              <span>{progress.progress_pct}%</span>
            </div>
            <Progress value={progress.progress_pct} size="sm" />
          </div>
        )}
      </Card>
    </Link>
  );
}
