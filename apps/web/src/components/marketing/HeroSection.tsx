'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { BookOpen } from 'lucide-react';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';

export function HeroSection() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  return (
    <section className="relative overflow-hidden" data-analytics="hero">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.08),transparent)]" />
      <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Finish the book.
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground font-serif leading-relaxed">
            {branding.product_name} is the writing studio that helps you plan, write, stay accountable, and
            finally finish your book — with the tools, structure, and AI support to keep you moving.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            {feature_flags.standalone_auth && (
              <>
                <Button asChild size="lg" className="min-w-[200px]" data-analytics="cta-start-free">
                  <Link href={`${getAppBaseUrl()}/register`}>Start Free</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                  <Link href="#how-it-works">See How It Works</Link>
                </Button>
              </>
            )}
            {!feature_flags.standalone_auth && feature_flags.sso_ready && (
              <Button asChild size="lg" className="min-w-[200px]">
                <Link href={`${getAppBaseUrl()}/sso`}>Sign in</Link>
              </Button>
            )}
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            For fiction and non-fiction writers who want more than a blank page.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-6 text-sm font-medium text-muted-foreground">
            <span>Plan clearly.</span>
            <span>Write smoothly.</span>
            <span>Finish confidently.</span>
          </div>
        </div>
        <div className="mt-16 flex justify-center">
          <div
            className="relative w-full max-w-4xl overflow-hidden rounded-xl border border-border/60 bg-muted/50 shadow-xl"
            data-analytics="hero-preview"
          >
            <div className="aspect-video flex items-center justify-center bg-gradient-to-br from-muted to-muted/50">
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Your writing studio
                </p>
                <p className="mt-1 text-xs text-muted-foreground/80">
                  Plan, write, and finish in one place
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
