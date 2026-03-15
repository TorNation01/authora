import type { Metadata } from 'next';
import { HeroSection } from '@/components/marketing/HeroSection';
import { FeatureSection } from '@/components/marketing/FeatureSection';
import { UseCasesSection } from '@/components/marketing/UseCasesSection';
import { TestimonialsSection } from '@/components/marketing/TestimonialsSection';
import { FAQSection } from '@/components/marketing/FAQSection';
import { CTASection } from '@/components/marketing/CTASection';
import { NewsletterSection } from '@/components/marketing/NewsletterSection';

export const metadata: Metadata = {
  title: 'AUTHORA | Finish Your Book — Guided Writing Journey with AI',
  description:
    'Write your book and actually finish it. AUTHORA guides you from idea to finished manuscript with AI support, accountability, and all your writing tools in one place.',
  keywords: ['book writing', 'author tool', 'AI writing', 'finish your book', 'writing app', 'novel writing'],
  openGraph: {
    title: 'AUTHORA | Finish Your Book',
    description: 'Your guided writing journey from idea to finished book. AI support without overwhelm.',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AUTHORA | Finish Your Book',
    description: 'Your guided writing journey from idea to finished book.',
  },
};

export default function LandingPage() {
  return (
    <div data-page="landing">
      <HeroSection />
      <FeatureSection />
      <UseCasesSection />
      <TestimonialsSection />
      <FAQSection />
      <NewsletterSection />
      <CTASection />
    </div>
  );
}
