'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { BookOpen, Sparkles, Target, FileDown } from 'lucide-react';
import { useConfig } from '@/contexts/ConfigProvider';

export function LandingContent() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  if (!feature_flags.standalone_landing && config.is_anakatech) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <h1 className="font-serif text-2xl font-bold text-foreground">{branding.product_name}</h1>
        <p className="mt-2 text-muted-foreground">{branding.tagline}</p>
        <div className="mt-8 flex gap-4">
          <Button asChild>
            <Link href={feature_flags.sso_ready ? '/sso' : '/login'}>Sign in</Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
        <div className="relative mx-auto max-w-6xl px-4 py-16 sm:px-6 sm:py-24 lg:px-8">
          <div className="text-center">
            <h1 className="font-serif text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl">
              Your writing sanctuary
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground font-serif leading-relaxed">
              {branding.product_name} guides you from idea to finished book. Plan, write, and export
              with calm focus—supported by AI when you need it.
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              {feature_flags.standalone_auth && (
                <>
                  <Button asChild size="lg" className="min-w-[180px]">
                    <Link href="/register">Start writing free</Link>
                  </Button>
                  <Button asChild variant="outline" size="lg" className="min-w-[180px]">
                    <Link href="/login">Sign in</Link>
                  </Button>
                </>
              )}
              {!feature_flags.standalone_auth && feature_flags.sso_ready && (
                <Button asChild size="lg" className="min-w-[180px]">
                  <Link href="/sso">Sign in</Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      <section className="border-t border-border/60 bg-muted/30 py-20">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
            <FeatureCard
              icon={<BookOpen className="h-8 w-8 text-primary" />}
              title="Guided planning"
              description="Fiction or non-fiction—structured planners help you outline before you write."
            />
            <FeatureCard
              icon={<Sparkles className="h-8 w-8 text-primary" />}
              title="AI when you need it"
              description="Stuck? Get suggestions and ideas. AI assists—you stay in control."
            />
            <FeatureCard
              icon={<Target className="h-8 w-8 text-primary" />}
              title="Stay accountable"
              description="Goals and reminders that feel supportive, not punishing."
            />
            <FeatureCard
              icon={<FileDown className="h-8 w-8 text-primary" />}
              title="Export ready"
              description="DOCX, PDF, EPUB. One click to share or publish."
            />
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="mx-auto max-w-3xl px-4 text-center">
          <h2 className="font-serif text-2xl font-semibold text-foreground sm:text-3xl">
            Ready to write your book?
          </h2>
          <p className="mt-4 text-muted-foreground">
            Join authors who finish. No credit card required.
          </p>
          {feature_flags.standalone_auth && (
            <Button asChild size="lg" className="mt-6">
              <Link href="/register">Create your account</Link>
            </Button>
          )}
        </div>
      </section>

      <footer className="border-t border-border/60 py-8">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <span className="font-serif text-sm font-medium text-muted-foreground">
              {branding.product_name}
            </span>
            <div className="flex gap-6 text-sm text-muted-foreground">
              {feature_flags.standalone_auth && (
                <>
                  <Link href="/login" className="hover:text-foreground">Sign in</Link>
                </>
              )}
              {feature_flags.standalone_setup_wizard && (
                <Link href="/setup" className="hover:text-foreground">Setup</Link>
              )}
              {branding.show_powered_by && (
                <span className="text-muted-foreground/70">Powered by AUTHORA</span>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="card-sanctuary p-6">
      <div className="mb-4">{icon}</div>
      <h3 className="font-semibold text-foreground">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
}
