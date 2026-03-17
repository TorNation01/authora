'use client';

import Link from 'next/link';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { Shield, Lock, FileText, PenLine } from 'lucide-react';
import { CTAPair } from '@/components/public/CTAPair';
import { CTA_MICROCOPY } from '@/content/cta-copy';

const TRUST_ITEMS = [
  { icon: Shield, label: 'Secure' },
  { icon: Lock, label: 'Private' },
  { icon: FileText, label: 'Your work stays yours' },
  { icon: PenLine, label: 'Built for real writers' },
];

const FOOTER_LINKS = {
  product: [
    { href: '/pricing', label: 'Pricing' },
    { href: '/features', label: 'Features' },
    { href: '/help', label: 'Help' },
    { href: '/story-integrity-engine', label: 'Story Integrity Engine' },
    { href: '/story-density-engine', label: 'Story Density Engine' },
    { href: '/for-fiction-writers', label: 'For Fiction Writers' },
    { href: '/for-nonfiction-writers', label: 'For Non-Fiction Writers' },
    { href: '/faq', label: 'FAQ' },
  ],
  legal: [
    { href: '/privacy', label: 'Privacy' },
    { href: '/terms', label: 'Terms' },
  ],
  support: [
    { href: '/contact', label: 'Contact' },
  ],
};

export function MarketingFooter() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  return (
    <footer
      className="footer-public"
      data-analytics="marketing-footer"
    >
      <div className="mx-auto max-w-7xl px-[var(--section-padding-x)] py-16">
        {/* Trust badges */}
        <div className="flex flex-wrap justify-center gap-8 mb-12">
          {TRUST_ITEMS.map((item) => (
            <div
              key={item.label}
              className="flex items-center gap-2 text-sm text-muted-foreground"
            >
              <item.icon className="h-4 w-4 text-primary" />
              <span>{item.label}</span>
            </div>
          ))}
        </div>

        {/* Navigation grid */}
        <div className="flex flex-wrap justify-center gap-x-12 gap-y-8 mb-12">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">
              Product
            </p>
            <ul className="space-y-3">
              {FOOTER_LINKS.product.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">
              Legal
            </p>
            <ul className="space-y-3">
              {FOOTER_LINKS.legal.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-4">
              Support
            </p>
            <ul className="space-y-3">
              {FOOTER_LINKS.support.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Footer CTA */}
        {feature_flags.standalone_auth && (
          <div className="flex flex-col items-center gap-4 mb-12">
            <CTAPair
              primary="start-free"
              secondary="view-pricing"
              microcopy={CTA_MICROCOPY.footer}
              analyticsPrefix="footer-"
            />
            <Link
              href={`${getAppBaseUrl()}/login`}
              className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors"
            >
              Log in
            </Link>
          </div>
        )}

        {/* Copyright and microcopy */}
        <div className="text-center space-y-2">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} {branding.product_name}. All rights reserved.
          </p>
          <p className="text-xs text-muted-foreground/80 max-w-md mx-auto">
            authora.studio — marketing & public site · app.authora.studio — writing app
          </p>
        </div>
      </div>
    </footer>
  );
}
