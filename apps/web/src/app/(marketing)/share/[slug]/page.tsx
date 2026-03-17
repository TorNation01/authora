'use client';

import { useConfig } from '@/contexts/ConfigProvider';
import { api } from '@/lib/api';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ShareCard } from '@/components/viral/ShareCard';

interface ShareData {
  share_type: string;
  payload: Record<string, unknown>;
  card: {
    title: string;
    subtitle: string;
    cta: string;
    product_name: string;
    share_url: string;
  };
  share_url: string;
}

const SHARE_TYPE = ['progress', 'milestone', 'achievement', 'book_finished'] as const;

export default function SharePage() {
  const params = useParams();
  const slug = params?.slug as string;
  const { branding } = useConfig();
  const [data, setData] = useState<ShareData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;
    api<ShareData>(`/api/v1/growth/share/${slug}`)
      .then(setData)
      .catch(() => setError('Share not found'))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-muted/30">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground">Share not found</h1>
          <p className="mt-2 text-muted-foreground">This link may have expired.</p>
          <Link href="/" className="mt-4 inline-block text-primary hover:underline">
            Go to {branding?.product_name || 'AUTHORA'}
          </Link>
        </div>
      </div>
    );
  }

  const { card, share_url } = data;
  const productName = branding?.product_name || card.product_name || 'AUTHORA';
  const shareType = (SHARE_TYPE.includes(data.share_type as (typeof SHARE_TYPE)[number])
    ? data.share_type
    : 'milestone') as 'progress' | 'milestone' | 'achievement' | 'book_finished';

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-muted/50 to-background p-6">
      <ShareCard
        data={{
          title: card.title,
          subtitle: card.subtitle,
          shareType,
          productName,
        }}
        className="mx-auto"
      />
      <div className="mt-8 flex flex-col items-center gap-4 max-w-md w-full">
        <Link
          href="/register"
          className="inline-flex items-center justify-center rounded-md bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary-hover w-full transition-colors"
        >
          {card.cta}
        </Link>
        <p className="text-xs text-muted-foreground">Powered by {productName}</p>
        <div className="flex justify-center gap-6 pt-4 border-t border-border/60 w-full">
          <a
            href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(card.subtitle)}&url=${encodeURIComponent(share_url)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Share on X
          </a>
          <a
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(share_url)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Share on LinkedIn
          </a>
        </div>
      </div>
    </div>
  );
}
