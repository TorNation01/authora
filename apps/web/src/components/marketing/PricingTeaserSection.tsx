'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';

export function PricingTeaserSection() {
  const config = useConfig();
  const { feature_flags } = config;

  return (
    <section className="border-t border-border/60 bg-muted/30 py-20" data-analytics="pricing-teaser">
      <div className="mx-auto max-w-3xl px-4 text-center sm:px-6 lg:px-8">
        <h2 className="font-serif text-3xl font-bold text-foreground sm:text-4xl">
          Start simple. Upgrade when you are ready.
        </h2>
        <p className="mt-4 text-lg text-muted-foreground">
          Begin for free, then move into deeper writing support, stronger AI assistance, and more
          advanced finishing tools as your projects grow.
        </p>
        <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          {feature_flags.standalone_auth && (
            <>
              <Button asChild size="lg" className="min-w-[200px]">
                <Link href={`${getAppBaseUrl()}/register`}>Start Free</Link>
              </Button>
              <Button asChild variant="outline" size="lg" className="min-w-[200px]">
                <Link href="/pricing">View Pricing</Link>
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
