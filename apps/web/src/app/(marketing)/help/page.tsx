import type { Metadata } from 'next';
import Link from 'next/link';
import { ChevronRight } from 'lucide-react';
import { HELP_NAV, HELP_PAGES } from '@/content/help-pages';

export const metadata: Metadata = {
  title: 'Help center | Authora',
  description:
    'Clear, helpful guidance for writing with Authora. Learn features, get unstuck, and finish your book.',
};

export default function HelpIndexPage() {
  return (
    <div>
      <h1 className="font-serif text-3xl font-bold text-foreground">
        Help center
      </h1>
      <p className="mt-2 text-muted-foreground">
        Find answers when you need them. Simple language, step-by-step guidance, no overwhelm.
      </p>

      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        {HELP_PAGES.map((page) => (
          <Link
            key={page.slug}
            href={`/help/${page.slug}`}
            className="group flex items-start justify-between gap-4 rounded-xl border border-border/60 p-5 transition-colors hover:border-primary/30 hover:bg-muted/30"
          >
            <div>
              <h2 className="font-semibold text-foreground group-hover:text-primary">
                {page.title}
              </h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {page.description}
              </p>
            </div>
            <ChevronRight className="h-5 w-5 shrink-0 text-muted-foreground group-hover:text-primary" />
          </Link>
        ))}
      </div>
    </div>
  );
}
