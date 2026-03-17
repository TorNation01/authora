'use client';

import Link from 'next/link';
import { useConfig } from '@/contexts/ConfigProvider';
import { getAppBaseUrl } from '@/lib/config';
import { Shield, Lock, FileText, PenLine } from 'lucide-react';

const TRUST_ITEMS = [
  { icon: Shield, label: 'Secure' },
  { icon: Lock, label: 'Private' },
  { icon: FileText, label: 'Your work stays yours' },
  { icon: PenLine, label: 'Built for real writers' },
];

export function MarketingFooter() {
  const config = useConfig();
  const { branding, feature_flags } = config;

  return (
    <footer className="border-t border-border/60 bg-muted/30" data-analytics="marketing-footer">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-wrap justify-center gap-6 mb-10">
          {TRUST_ITEMS.map((item) => (
            <div key={item.label} className="flex items-center gap-2 text-sm text-muted-foreground">
              <item.icon className="h-4 w-4 text-primary" />
              <span>{item.label}</span>
            </div>
          ))}
        </div>
        <div className="flex flex-wrap justify-center gap-x-8 gap-y-2 text-sm">
          <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
            Privacy
          </Link>
          <Link href="/terms" className="text-muted-foreground hover:text-foreground">
            Terms
          </Link>
          <Link href="/contact" className="text-muted-foreground hover:text-foreground">
            Contact
          </Link>
          <Link href="/pricing" className="text-muted-foreground hover:text-foreground">
            Pricing
          </Link>
          {feature_flags.standalone_auth && (
            <>
              <Link href={`${getAppBaseUrl()}/login`} className="text-muted-foreground hover:text-foreground">
                Login
              </Link>
              <Link href={`${getAppBaseUrl()}/register`} className="text-muted-foreground hover:text-foreground">
                Sign up
              </Link>
            </>
          )}
        </div>
        <div className="mt-8 text-center">
          <span className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} {branding.product_name}. All rights reserved.
          </span>
        </div>
      </div>
    </footer>
  );
}
