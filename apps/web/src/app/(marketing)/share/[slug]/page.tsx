'use client';

import { useConfig } from '@/contexts/ConfigProvider';
import { api } from '@/lib/api';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';

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

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-muted/50 to-background p-4">
      <div className="max-w-md w-full bg-card rounded-xl shadow-lg border p-8 text-center">
        <h1 className="text-xl font-semibold text-foreground">{card.title}</h1>
        <p className="mt-2 text-muted-foreground">{card.subtitle}</p>
        <div className="mt-6 flex flex-col gap-3">
          <Link
            href="/register"
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            {card.cta}
          </Link>
          <p className="text-xs text-muted-foreground">
            Powered by {productName}
          </p>
        </div>
        <div className="mt-8 pt-6 border-t flex justify-center gap-4">
          <a
            href={`https://twitter.com/intent/tweet?text=${encodeURIComponent(card.subtitle)}&url=${encodeURIComponent(share_url)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Share on X
          </a>
          <a
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(share_url)}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-muted-foreground hover:text-foreground"
          >
            Share on LinkedIn
          </a>
        </div>
      </div>
    </div>
  );
}
