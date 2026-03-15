'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { BookOpen } from 'lucide-react';
import { useConfig } from '@/contexts/ConfigProvider';

export function HeroSection() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  return (
    <section className="relative overflow-hidden" data-analytics="hero">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,hsl(var(--primary)/0.08),transparent)]" />
      <div className="relative mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-28 lg:px-8">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm font-medium uppercase tracking-wider text-primary">
            Guided writing journey
          </p>
          <h1 className="mt-4 font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
            Finish your book
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground font-serif leading-relaxed">
            {branding.product_name} guides you from idea to finished manuscript. Plan, write, and export
            with AI support when you need it—without overwhelm. All your writing tools in one place.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            {feature_flags.standalone_auth && (
              <>
                <Button asChild size="lg" className="min-w-[200px]" data-analytics="cta-start-writing">
                  <Link href="/register">Start writing free</Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                  <Link href="/demo">Request demo</Link>
                </Button>
              </>
            )}
            {!feature_flags.standalone_auth && feature_flags.sso_ready && (
              <Button asChild size="lg" className="min-w-[200px]">
                <Link href="/sso">Sign in</Link>
              </Button>
            )}
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            No credit card required · Free to start
          </p>
        </div>
        {/* Screenshot/illustration placeholder */}
        <div className="mt-16 flex justify-center">
          <div
            className="relative w-full max-w-4xl overflow-hidden rounded-xl border border-border/60 bg-muted/50 shadow-xl"
            data-analytics="hero-screenshot-placeholder"
          >
            <div className="aspect-video flex items-center justify-center bg-gradient-to-br from-muted to-muted/50">
              <div className="text-center">
                <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10">
                  <BookOpen className="h-8 w-8 text-primary" />
                </div>
                <p className="text-sm font-medium text-muted-foreground">
                  Writing studio preview
                </p>
                <p className="mt-1 text-xs text-muted-foreground/80">
                  Screenshot or illustration placeholder
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
