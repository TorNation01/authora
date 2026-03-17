'use client';

import React, { useState, useRef, useCallback } from 'react';

const HTML2CANVAS_CDN =
  'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';

function loadHtml2Canvas(): Promise<
  (el: HTMLElement, opts?: { scale?: number; useCORS?: boolean; backgroundColor?: null; logging?: boolean }) => Promise<HTMLCanvasElement>
> {
  const w = typeof window === 'undefined' ? null : (window as Window & { html2canvas?: unknown });
  if (w?.html2canvas) return Promise.resolve(w.html2canvas as Awaited<ReturnType<typeof loadHtml2Canvas>>);
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = HTML2CANVAS_CDN;
    script.async = true;
    script.onload = () => {
      const h2c = (window as Window & { html2canvas?: unknown }).html2canvas;
      if (h2c) resolve(h2c as Awaited<ReturnType<typeof loadHtml2Canvas>>);
      else reject(new Error('html2canvas not loaded'));
    };
    script.onerror = () => reject(new Error('Failed to load html2canvas'));
    document.head.appendChild(script);
  });
}
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ShareCard, type ShareCardData } from './ShareCard';
import { Share2, Copy, Check, Download, ExternalLink } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { useConfig } from '@/contexts/ConfigProvider';

export type ShareType = 'progress' | 'milestone' | 'achievement' | 'book_finished';

interface ShareDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  shareType: ShareType;
  payload: Record<string, unknown>;
  displayName?: string;
  /** Pre-built card data when we already have API response */
  cardData?: ShareCardData | null;
  shareUrl?: string | null;
}

export function ShareDialog({
  open,
  onOpenChange,
  shareType,
  payload,
  displayName,
  cardData: initialCardData,
  shareUrl: initialShareUrl,
}: ShareDialogProps) {
  const { toast } = useToast();
  const config = useConfig();
  const cardRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(initialShareUrl ?? null);
  const [cardData, setCardData] = useState<ShareCardData | null>(initialCardData ?? null);

  const productName = config.branding?.product_name ?? 'AUTHORA';

  const createShare = useCallback(async () => {
    if (shareUrl && cardData) return;
    setLoading(true);
    try {
      const res = await api<{
        share_url: string;
        card: { title: string; subtitle: string };
        caption: string;
      }>('/api/v1/growth/share', {
        method: 'POST',
        body: JSON.stringify({
          share_type: shareType,
          payload: { ...payload, display_name: displayName ?? 'A writer' },
          expires_days: 90,
        }),
      });
      setShareUrl(res.share_url);
      setCardData({
        title: res.card.title,
        subtitle: res.card.subtitle,
        shareType,
        productName,
      });
    } catch {
      toast({ title: 'Sharing unavailable', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  }, [shareType, payload, displayName, productName, shareUrl, cardData, toast]);

  React.useEffect(() => {
    if (open && !shareUrl && !loading) {
      createShare();
    }
  }, [open, createShare, shareUrl, loading]);

  const handleCopyLink = async () => {
    if (!shareUrl) return;
    await navigator.clipboard.writeText(shareUrl);
    setCopied(true);
    toast({ title: 'Link copied' });
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadImage = async () => {
    if (!cardRef.current || !cardData) return;
    try {
      const h2c = await loadHtml2Canvas();
      const canvas = await h2c(cardRef.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: null,
        logging: false,
      });
      const link = document.createElement('a');
      link.download = `authora-share-${shareType}-${Date.now()}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      toast({ title: 'Image saved' });
    } catch {
      toast({ title: 'Download failed', variant: 'destructive' });
    }
  };

  const twitterUrl = shareUrl
    ? `https://twitter.com/intent/tweet?text=${encodeURIComponent(cardData?.subtitle ?? '')}&url=${encodeURIComponent(shareUrl)}`
    : null;
  const linkedinUrl = shareUrl
    ? `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`
    : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5 text-primary" />
            Share your progress
          </DialogTitle>
          <DialogDescription>
            Celebrate your achievement. Copy the link, download the image, or share on social.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {loading ? (
            <div className="flex h-[280px] items-center justify-center rounded-2xl border-2 border-dashed border-muted bg-muted/30">
              <p className="text-sm text-muted-foreground">Creating share...</p>
            </div>
          ) : cardData ? (
            <div className="flex justify-center">
              <ShareCard ref={cardRef} data={cardData} />
            </div>
          ) : null}

          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyLink}
              disabled={!shareUrl}
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
              <span className="ml-1.5">{copied ? 'Copied!' : 'Copy link'}</span>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownloadImage}
              disabled={!cardData}
            >
              <Download className="h-4 w-4" />
              <span className="ml-1.5">Download image</span>
            </Button>
            {twitterUrl && (
              <Button variant="outline" size="sm" asChild>
                <a href={twitterUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  <span className="ml-1.5">Share on X</span>
                </a>
              </Button>
            )}
            {linkedinUrl && (
              <Button variant="outline" size="sm" asChild>
                <a href={linkedinUrl} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  <span className="ml-1.5">Share on LinkedIn</span>
                </a>
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
