'use client';

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Inbox, Loader2, Send } from 'lucide-react';
import { cn } from '@/lib/utils';
import { IDEA_CAPTURE } from '@/content/vault-copy';

interface VaultQuickCaptureProps {
  projectId: string;
  onCreated?: () => void;
  placeholder?: string;
  className?: string;
}

export function VaultQuickCapture({
  projectId,
  onCreated,
  placeholder = IDEA_CAPTURE.placeholder,
  className,
}: VaultQuickCaptureProps) {
  const [value, setValue] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  const handleCapture = async () => {
    const text = value.trim();
    if (!text) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/vault/ideas`, {
        method: 'POST',
        body: JSON.stringify({
          title: text.slice(0, 80) + (text.length > 80 ? '…' : ''),
          content: text,
          idea_type: 'quick_note',
          status: 'raw_idea',
        }),
      });
      setValue('');
      onCreated?.();
      toast({ title: IDEA_CAPTURE.captured });
    } catch (e) {
      toast({
        title: 'Couldn\'t save',
        description: e instanceof Error ? e.message : 'Try again.',
        variant: 'destructive',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card variant="soft" className={cn('overflow-hidden', className)}>
      <CardContent className="p-0">
        <div className="flex items-stretch gap-0">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center bg-primary/5 text-primary">
            <Inbox className="h-5 w-5" />
          </div>
          <input
            type="text"
            placeholder={placeholder}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCapture()}
            className="flex-1 min-w-0 bg-transparent px-4 py-3 text-sm placeholder:text-muted-foreground focus:outline-none"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCapture}
            disabled={saving || !value.trim()}
            className="shrink-0 rounded-l-none"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
