'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';

export function CTASection() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  return (
    <section className="py-20" data-analytics="cta">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Ready to write your book?
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Join authors who finish. No credit card required.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          {feature_flags.standalone_auth && (
            <>
              <Button asChild size="lg" className="min-w-[200px]">
                <Link href={`${getAppBaseUrl()}/register`}>Create your account</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                <Link href="/demo">Request a demo</Link>
              </Button>
            </>
          )}
          {!feature_flags.standalone_auth && feature_flags.sso_ready && (
            <Button asChild size="lg" className="min-w-[200px]">
              <Link href={`${getAppBaseUrl()}/sso`}>Sign in</Link>
            </Button>
          )}
        </div>
      </div>
    </section>
  );
}
