'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';

export function CTASection() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section className="py-20" data-analytics="cta">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Your book is not finished yet — but it can be.
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Authora gives you the tools, structure, and support to get there.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          {feature_flags.standalone_auth && (
            <>
              <Button asChild size="lg" className="min-w-[200px]">
                <Link href={`${getAppBaseUrl()}/register`}>Start Writing Free</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                <Link href={`${getAppBaseUrl()}/register`}>Create Your First Book</Link>
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
          Stop circling the idea. Start finishing the book.
        </p>
      </div>
    </section>
  );
}
