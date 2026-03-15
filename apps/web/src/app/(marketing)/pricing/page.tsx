import type { Metadata } from 'next';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Check } from 'lucide-react';
import { PlanComparison } from '@/components/billing/PlanComparison';

export const metadata: Metadata = {
  title: 'Pricing | AUTHORA',
  description: 'Simple, transparent pricing. Start free. Upgrade when you need more.',
};

const PLANS = [
  {
    id: 'free',
    slug: 'free',
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Get started. No credit card.',
    limits: {
      projects: 1,
      books: 3,
      ai_actions: 20,
      exports: 5,
      formats: 'DOCX, TXT',
    },
    features: [
      '1 project',
      '3 books',
      'Guided planning',
      'Distraction-free editor',
      'Notes & research',
      'Export to DOCX, TXT',
      'Community support',
    ],
    cta: 'Start free',
    href: '/register',
    featured: false,
  },
  {
    id: 'premium',
    slug: 'premium',
    name: 'Premium',
    price: 'TBD',
    period: '/month',
    description: 'For serious authors who want to finish.',
    limits: {
      projects: 'Unlimited',
      books: 'Unlimited',
      ai_actions: 500,
      exports: 50,
      formats: 'DOCX, PDF, EPUB, TXT',
    },
    features: [
      'Unlimited projects & books',
      'All templates',
      'AI assistance',
      'Ghostwriter mode',
      'Goals & accountability',
      'Export: DOCX, PDF, EPUB',
      'Publishing prep tools',
      'Priority support',
    ],
    cta: 'Coming soon',
    href: '/contact',
    featured: true,
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
      <div className="mt-16 grid gap-8 lg:grid-cols-2">
        {PLANS.map((plan) => (
          <div
            key={plan.id}
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
      <div className="mt-16">
        <h2 className="font-serif text-2xl font-semibold text-center mb-8">
          Compare plans
        </h2>
        <PlanComparison />
      </div>
      <p className="mt-12 text-center text-sm text-muted-foreground">
        Premium pricing coming soon. Contact us for early access.
      </p>
    </div>
  );
}
