'use client';

import { api } from '@/lib/api';
import { Share2, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ShareButtonProps {
  shareType: 'progress' | 'milestone' | 'achievement' | 'book_finished';
  payload: Record<string, unknown>;
  displayName?: string;
  onShare?: (url: string) => void;
  className?: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
}

export function ShareButton({
  shareType,
  payload,
  displayName,
  onShare,
  className,
  variant = 'ghost',
  size = 'sm',
}: ShareButtonProps) {
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  async function handleShare() {
    setLoading(true);
    try {
      const res = await api<{ share_url: string; caption: string; social_links: Record<string, string> }>(
        '/api/v1/growth/share',
        {
          method: 'POST',
          body: JSON.stringify({
            share_type: shareType,
            payload: { ...payload, display_name: displayName },
            expires_days: 90,
          }),
        }
      );
      setShareUrl(res.share_url);
      onShare?.(res.share_url);
    } catch {
      // Silently fail (user may not have growth enabled)
    } finally {
      setLoading(false);
    }
  }

  async function copyUrl() {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  if (!shareUrl) {
    return (
      <Button
        variant={variant}
        size={size}
        className={className}
        onClick={handleShare}
        disabled={loading}
      >
        <Share2 className="h-4 w-4" />
        {size !== 'icon' && <span className="ml-1">{loading ? 'Creating...' : 'Share'}</span>}
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant={variant} size={size} className={className}>
          <Share2 className="h-4 w-4" />
          {size !== 'icon' && <span className="ml-1">Share</span>}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={copyUrl}>
          {copied ? <Check className="h-4 w-4 mr-2" /> : <Copy className="h-4 w-4 mr-2" />}
          {copied ? 'Copied!' : 'Copy link'}
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <a
            href={`https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Share on X
          </a>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <a
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Share on LinkedIn
          </a>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
