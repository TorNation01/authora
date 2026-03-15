import type { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Check } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Pricing | AUTHORA',
  description: 'Simple, transparent pricing. Start free. Upgrade when you need more.',
};

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Get started. No credit card.',
    features: [
      '1 project',
      '3 books',
      'Basic planning',
      'Export to DOCX, TXT',
      'Community support',
    ],
    cta: 'Start free',
    href: '/register',
    featured: false,
  },
  {
    name: 'Pro',
    price: 'TBD',
    period: '/month',
    description: 'For serious authors who want to finish.',
    features: [
      'Unlimited projects & books',
      'All templates',
      'AI assistance',
      'Accountability & goals',
      'Export: DOCX, PDF, EPUB',
      'Priority support',
    ],
    cta: 'Coming soon',
    href: '#',
    featured: true,
  },
  {
    name: 'Team',
    price: 'TBD',
    period: '/month',
    description: 'For writing groups and small presses.',
    features: [
      'Everything in Pro',
      'Shared workspaces',
      'Admin controls',
      'SSO (optional)',
    ],
    cta: 'Contact us',
    href: '/contact',
    featured: false,
  },
];

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <h1 className="font-serif text-4xl font-bold text-foreground sm:text-5xl">
          Simple pricing
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          Start free. Upgrade when you need more. No surprises.
        </p>
      </div>
      <div className="mt-16 grid gap-8 lg:grid-cols-3">
        {PLANS.map((plan) => (
          <div
            key={plan.name}
            className={`card-sanctuary rounded-xl p-8 ${
              plan.featured ? 'ring-2 ring-primary shadow-lg' : ''
            }`}
          >
            {plan.featured && (
              <span className="inline-block rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
                Most popular
              </span>
            )}
            <h2 className="mt-4 font-serif text-2xl font-semibold text-foreground">
              {plan.name}
            </h2>
            <div className="mt-2 flex items-baseline gap-1">
              <span className="text-3xl font-bold text-foreground">{plan.price}</span>
              <span className="text-muted-foreground">{plan.period}</span>
            </div>
            <p className="mt-2 text-sm text-muted-foreground">{plan.description}</p>
            <ul className="mt-6 space-y-3">
              {plan.features.map((f) => (
                <li key={f} className="flex items-start gap-3 text-sm">
                  <Check className="h-5 w-5 shrink-0 text-primary" />
                  {f}
                </li>
              ))}
            </ul>
            <Button
              asChild
              variant={plan.featured ? 'default' : 'outline'}
              className="mt-8 w-full"
            >
              <Link href={plan.href}>{plan.cta}</Link>
            </Button>
          </div>
        ))}
      </div>
      <p className="mt-12 text-center text-sm text-muted-foreground">
        Pricing structure ready. Update with actual plans and pricing when available.
      </p>
    </div>
  );
}
