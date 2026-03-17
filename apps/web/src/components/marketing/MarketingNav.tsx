'use client';

import Link from 'next/link';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { Menu, X } from 'lucide-react';

const NAV_LINKS = [
  { href: '/#how-it-works', label: 'How It Works' },
  { href: '/features', label: 'Features' },
  { href: '/pricing', label: 'Pricing' },
  { href: '/faq', label: 'FAQ' },
  { href: '/contact', label: 'Contact' },
];

export function MarketingNav() {
  const config = useConfig();
  const [mobileOpen, setMobileOpen] = useState(false);
  const { branding, feature_flags } = config;

  return (
    <header
      className="header-public supports-[backdrop-filter]:bg-background/80"
      data-analytics="marketing-nav"
    >
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link
          href="/"
          className="font-serif text-xl font-semibold text-foreground transition-opacity hover:opacity-90"
        >
          {branding.product_name}
        </Link>

        <div className="hidden md:flex md:items-center md:gap-8">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-4">
          {feature_flags.standalone_auth && (
            <>
              <Link
                href={`${getAppBaseUrl()}/login`}
                className="hidden text-sm font-medium text-muted-foreground transition-colors hover:text-foreground sm:block"
              >
                Sign in
              </Link>
              <Button asChild size="sm" className="h-9">
                <Link href={`${getAppBaseUrl()}/register`}>Start Writing Free</Link>
              </Button>
            </>
          )}
          {!feature_flags.standalone_auth && feature_flags.sso_ready && (
            <Button asChild size="sm" className="h-9">
              <Link href={`${getAppBaseUrl()}/sso`}>Sign in</Link>
            </Button>
          )}
          <button
            type="button"
            className="rounded-md p-2 text-muted-foreground transition-colors hover:bg-white/5 hover:text-foreground md:hidden"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </nav>

      {mobileOpen && (
        <div className="border-t border-white/[0.06] bg-background px-4 py-4 md:hidden">
          <div className="flex flex-col gap-4">
            {NAV_LINKS.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            {feature_flags.standalone_auth && (
              <div className="flex gap-3 pt-2 border-t border-white/[0.06]">
                <Link
                  href={`${getAppBaseUrl()}/login`}
                  className="text-sm font-medium"
                  onClick={() => setMobileOpen(false)}
                >
                  Sign in
                </Link>
                <Button asChild size="sm">
                  <Link href={`${getAppBaseUrl()}/register`} onClick={() => setMobileOpen(false)}>
                    Start Writing Free
                  </Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
